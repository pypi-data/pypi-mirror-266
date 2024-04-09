import io
import json
import logging
import numpy as np
import zipfile
from typing import Any, Dict, List, Tuple

from .constraints import Constraints
from .errors import (
    ConstraintAlreadySetError,
    MissingVariableError,
    MissingObjectiveError,
    ObjectiveAlreadySetError,
    OptimizeError
)
from .objective import Objective, Target
from .optimize_response import OptimizeResponse
from .manifest import Manifest
from .variable import BinaryVariableVector, BipolarVariableVector, IntegerVariableVector, Vtype
from .._client import api_model, Client
from .._storage import ManagedStorage, StorageClient
from .numpy_util import (
    is_ndarray_binary,
    is_upperbound_bigger_equal_lowerbound,
    ndarray_contains_nan_inf,
    reshape_to_2d,
    validate_cardinalities
)
from .variable_list import VariableVectorList

log = logging.getLogger("TitanQ")

_TITANQ_BASE_URL = "https://titanq.infinityq.io"


class Model:
    """
    Root object to define a problem to be optimize
    """

    def __init__(
        self,
        *,
        api_key: str,
        storage_client: StorageClient = None,
        base_server_url: str = _TITANQ_BASE_URL
        ) -> None:
        """
        Initiate the model with a storage client depending on the provided arguments.

        If the storage_client is missing, the storage will be managed by TitanQ.

        NOTE: the storage manged by TitanQ supports weight matrices with a size up to 10k

        :param api_key: TitanQ api key to access the service.
        :param storage_client: Storage to choose in order to store some items
        :param base_server_url: TitanQ server url


        Example
        ~~~~~~~
        ..  highlight:: python
        ..  code-block:: python
        from titanq import Model, S3Storage

        # s3 storage on AWS
        model = Model(
            api_key="{insert API key here}",
            storage_client=S3Storage(
                access_key="{insert aws bucket access key here}",
                secret_key="{insert aws bucket secret key here}",
                bucket_name="{insert bucket name here}"
            )
        )

        # managed Storage (Up to 10k variables only)
        model = Model(api_key="{insert API key here}")
        """
        self._variables = VariableVectorList()
        self._objective: Objective = None
        self._constraints = Constraints()
        self._titanq_client = Client(api_key, base_server_url)
        self._manifest: Manifest = Manifest()

        # the user chose a managed storage or left it as default
        if storage_client is None:
            storage_client = ManagedStorage(self._titanq_client)

        self._storage_client = storage_client


    def add_variable_vector(self, name='', size=1, vtype=Vtype.BINARY, variable_bounds: List[Tuple[int, int]]=[]):
        """
        Add a vector of variable to the model. Only a single vector of variables can be set.
        Calling this method again will override the current vector of variables

        :param name: The name given to this variable vector.
        :param size: The size of the vector.
        :param vtype: Type of the variables inside the vector.

        :raise MaximumVariableLimitError: If a variable is already defined.
        :raise ValueError: If the size of the vector is < 1.

        Example
        ~~~~~~~
        ..  highlight:: python
        ..  code-block:: python
        import numpy as np
        from titanq import Model, Vtype

        # set up model
        ...

        model.add_variable_vector('x', size, Vtype.BINARY)
        """
        # validation
        if not self._constraints.is_empty():
            raise ConstraintAlreadySetError("Cannot add additional variable once constraints have been defined")

        if self._objective is not None:
            raise ObjectiveAlreadySetError("Cannot add additional variable once objective have been defined")

        # create the Variable vector
        if vtype is Vtype.BINARY:
            if variable_bounds:
                raise ValueError("variable_bounds is not supported with Vtype.BINARY")
            variables = BinaryVariableVector(name, size)

        elif vtype is Vtype.BIPOLAR:
            if variable_bounds:
                raise ValueError("variable_bounds is not supported with Vtype.BIPOLAR")
            variables = BipolarVariableVector(name, size)

        elif vtype is Vtype.INTEGER:
            variables = IntegerVariableVector(name, size, variable_bounds)

        else:
            raise NotImplementedError(f"Unsupported variable type: {vtype}")

        self._variables.add(variables)
        self._constraints.augment_size(size)

        log.debug(f"add variable name='{name}', type={str(vtype)}, size={size}.")



    def set_objective_matrices(self, weights: np.ndarray, bias: np.ndarray, target=Target.MINIMIZE):
        """
        Set the objective matrices for the model.

        :param weights: The quadratic objective matrix, **this matrix needs to be symmetrical**
        :type weights: a NumPy 2-D dense ndarray (must be float32)

        :param bias: The linear constraint vector
        :type bias:  a NumPy 1-D ndarray

        :param target: The target of this objective matrix.
        :type target: Target Enum

        :raise MissingVariableError: If no variable have been added to the model.
        :raise ObjectiveAlreadySetError: If an objective has already been setted in this model.
        :raise ValueError: If the weights shape or the bias shape does not fit the variable in the model.
        :raise ValueError: If the weights or bias data type is not f32.

        Example
        ~~~~~~~
        ..  highlight:: python
        ..  code-block:: python
        from titanq import Model, Target

        edges = {0:[4,5,6,7], 1:[4,5,6,7], 2:[4,5,6,7], 3:[4,5,6,7], 4:[0,1,2,3], 5:[0,1,2,3], 6:[0,1,2,3], 7:[0,1,2,3]}
        size = len(edges)

        # construct the weight matrix from the edges list
        weights = np.zeros((size, size), dtype=np.float32)
        for root, connections in edges.items():
            for c in connections:
                weights[root][c] = 1

        # construct the bias vector (Uniform weighting across all nodes)
        bias = np.asarray([0]*size, dtype=np.float32)

        # set up model
        ...

        model.set_objective_matrices(weights, bias, Target.MINIMIZE)
        """

        if self._variables.n_variables() == 0:
            raise MissingVariableError("Cannot set objective before adding a variable to the model.")

        if self._objective is not None:
            raise ObjectiveAlreadySetError("An objective has already have been set for this model.")

        log.debug(f"set objective matrix and bias vector.")

        self._objective = Objective(self._variables.total_variable_size(), weights, bias, target)


    def set_constraints_matrices(self, constraint_weights: np.ndarray, constraint_bounds: np.ndarray):
        """
        Set the constraints matrices for the model.

        :param constraint_weights: The constraint_weights matrix of shape (M, N) where M the number of constraints and N is the number of variables
        :type constraint_weights: a NumPy 2-D dense ndarray (must be float32)

        :param constraint_bounds: The constraint_bounds vector of shape (M,2) where M is the number of constraints
        :type constraint_bounds:  a NumPy 1-D ndarray (must be float32)

        :raise MissingVariableError: If no variable have been added to the model.
        :raise ValueError: If the constraint_weights shape or the constraint_bounds shape does not fit the expected shape of this model.
        :raise ValueError: If the constraint_weights or constraint_bounds data type is not f32.
        """
        if self._variables.n_variables() == 0:
            raise MissingVariableError("Cannot set constraints before adding a variable to the model.")

        log.debug(f"set weights constraints matrix and bias constraints vector.")
        self._constraints.set_constraint_matrices(constraint_weights, constraint_bounds)


    def add_set_partitioning_constraints_matrix(self, constraint_mask: np.ndarray):
        """
        Adds set partitioning constraints in matrix format to the model.

        :param constraint_mask: The constraint_mask matrix of shape (M, N) where M the number of constraints and N is the number of variables.
        :type constraint_mask: A NumPy 2-D dense ndarray (must be binary)

        :raise MissingVariableError: If no variable have been added to the model.
        :raise MaximumConstraintLimitError: The number of constraint exeed the limit.
        :raise ConstraintSizeError: If the constraint_mask shape does not fit the expected shape of this model.
        :raise ValueError: If the constraint_mask data type is not binary.

        Example
        ~~~~~~~
        ..  highlight:: python
        ..  code-block:: python

        from titanq import Model

        # set up model
        ...

        constraint_mask = np.array([[1, 1, 1, 0, 1], [1, 1, 1, 1, 0]])
        model.add_set_partitioning_constraints_matrix(constraint_mask)
        """
        if self._variables.n_variables() == 0:
            raise MissingVariableError("Cannot set constraints before adding a variable to the model.")

        if constraint_mask.ndim == 1:
            raise ValueError(
                "Cannot use add_set_partitioning_constraints_matrix() function with a vector, " \
                "please use add_set_partitioning_constraint() insead")

        if not is_ndarray_binary(constraint_mask):
            raise ValueError(f"Cannot add a constraint if the values are not in binary.")

        self._constraints.add_constraint(
            constraint_weights=constraint_mask,
            constraint_bounds=np.ones((constraint_mask.shape[0],2))
        )
        self._manifest.activate_set_partitioning_constraint()

    def add_set_partitioning_constraint(self, constraint_mask: np.ndarray):
        """
        Adds set partitioning constraint vector to the model.

        :param constraint_mask: The constraint_mask vector of shape (N,) where N is the number of variables.
        :type constraint_mask: A NumPy 1-D dense ndarray (must be binary)

        :raise MissingVariableError: If no variable have been added to the model.
        :raises MaximumConstraintLimitError: The number of constraint exeed the limit.
        :raise ConstraintSizeError: If the constraint_mask shape does not fit the expected shape of this model.
        :raise ValueError: If the constraint_mask data type is not binary.

        Example
        ~~~~~~~
        ..  highlight:: python
        ..  code-block:: python

        from titanq import Model

        # set up model
        ...

        constraint_mask = np.array([1, 1, 1, 0, 1])
        model.add_set_partitioning_constraint(constraint_mask)
        """
        if constraint_mask.ndim > 1:
            raise ValueError(
                "Cannot use this add_set_partitioning_constraint() function with a matrix, " \
                "please use add_set_partitioning_constraints_matrix() insead")

        self.add_set_partitioning_constraints_matrix(reshape_to_2d(constraint_mask))


    def add_cardinality_constraints_matrix(self, constraint_mask: np.ndarray, cardinalities: np.ndarray):
        """
        Adds cardinality constraints in matrix format to the model.

        :param constraint_mask: The constraint_mask matrix of shape (M, N) where M the number of constraints and N is the number of variables.
        :type constraint_mask: a NumPy 2-D dense ndarray (must be binary)

        :param cardinalities: The constraint_rhs vector of shape (M,) where M is the number of constraints
        :type cardinalities:  a NumPy 1-D ndarray (must be non-zero unsigned integer)

        :raise MissingVariableError: If no variable have been added to the model.
        :raises MaximumConstraintLimitError: The number of constraint exeed the limit.
        :raise ConstraintSizeError: If the constraint_mask shape or the constraint_rhs shape does not fit the expected shape of this model.
        :raise ValueError: If the constraint_mask is not binary or cardinalities data type is not unsigned integer.

        Example
        ~~~~~~~
        ..  highlight:: python
        ..  code-block:: python

        from titanq import Model

        # set up model
        ...

        constraint_mask = np.array([[1, 1, 1, 0, 1], [1, 1, 1, 1, 0]])
        cardinalities = np.array([3, 2])
        model.add_cardinality_constraints_matrix(constraint_mask, cardinalities)
        """
        if self._variables.n_variables() == 0:
            raise MissingVariableError("Cannot set constraints before adding a variable to the model.")

        if constraint_mask.ndim == 1:
            raise ValueError(
                "Cannot use add_cardinality_constraints_matrix() function with a vector, " \
                "please use add_cardinality_constraint() insead")

        if cardinalities.ndim != 1:
            raise ValueError(f"Cannot set constraints if cardinalities is not a NumPy 1-D dense ndarray")

        if not np.issubdtype(cardinalities.dtype, np.integer):
            raise ValueError("Found cardinalities data types not integer")

        if not np.all(cardinalities > 0):
            raise ValueError("Found cardinalities data types not unsigned integer")

        if not is_ndarray_binary(constraint_mask):
            raise ValueError(f"Cannot add a constraint if the values are not in binary.")

        if cardinalities.shape[0] != constraint_mask.shape[0]:
            raise ValueError(
                f"Cannot set constraints if cardinalities shape is not the same as the expected shape of this model." \
                f" Got cardinalities shape: {cardinalities.shape[1]}, constraint mask shape: {constraint_mask.size()}.")

        validate_cardinalities(constraint_mask, cardinalities)

        self._constraints.add_constraint(
            constraint_weights=constraint_mask,
            constraint_bounds=np.repeat(cardinalities, 2).reshape(-1, 2)
        )
        self._manifest.activate_cardinality_constraint()


    def add_cardinality_constraint(self, constraint_mask: np.ndarray, cardinality: int):
        """
        Adds cardinality constraints vector to the model.

        :param constraint_mask: The constraint_mask vector of shape (N,) where N is the number of variables.
        :type constraint_mask: a NumPy 1-D dense ndarray (must be binary)

        :param cardinality: The constraint_rhs vector of shape (M,) where M is the number of constraints
        :type cardinality:  a non-zero unsigned integer

        :raise MissingVariableError: If no variable have been added to the model.
        :raises MaximumConstraintLimitError: The number of constraint exeed the limit.
        :raise ConstraintSizeError: If the constraint_mask shape or the constraint_rhs shape does not fit the expected shape of this model.
        :raise ValueError: If the constraint_mask is not binary or constraint_rhs data type is not unsigned integer.

        Example
        ~~~~~~~
        ..  highlight:: python
        ..  code-block:: python

        from titanq import Model

        # set up model
        ...

        constraint_mask = np.array([1, 1, 1, 0, 1])
        cardinalities = 3
        model.add_cardinality_constraint(constraint_mask, cardinality)
        """
        if constraint_mask.ndim > 1:
            raise ValueError(
                "Cannot use add_cardinality_constraint() function with a matrix, " \
                "please use add_cardinality_constraints_matrix() insead")

        self.add_cardinality_constraints_matrix(reshape_to_2d(constraint_mask), np.full((1,), cardinality))


    def add_equality_constraints_matrix(self, constraint_mask: np.ndarray, limit: np.ndarray) -> None:
        """
        Adds an equality constraint matrix to the model.

        :param constraint_mask: The constraint_mask vector of shape (M, N) where M the number of constraints and N is the number of variables.
        :type constraint_mask: A NumPy 2-D dense ndarray (float32)
        :param limit: The limit vector of shape (M,) where M is the number of constraints
        :type limit: A NumPy 1-D array (float32)

        :raise MissingVariableError: If no variable have been added to the model.
        :raises MaximumConstraintLimitError: The number of constraint exceed the limit.
        :raise ValueError: If the constraint_mask shape does not fit the expected shape of this model.
        :raise ValueError: If the constraint_mask or limit contains irregular format ('NaN' or 'inf')
        """
        if self._variables.n_variables() == 0:
            raise MissingVariableError("Cannot set constraints before adding a variable to the model.")

        if constraint_mask.dtype != np.float32 or limit.dtype != np.float32:
            raise ValueError(f"Input parameters must be float32, got Constraint mask: {constraint_mask.dtype}, Limit: {limit.dtype}")

        if constraint_mask.ndim == 1:
            raise ValueError(
                "Cannot use add_equality_constraint_matrix() function with a vector, " \
                "please use add_equality_constraint() insead")

        if ndarray_contains_nan_inf(constraint_mask):
            raise ValueError("Constraint mask contains NaN  or inf values")

        if limit.ndim != 1:
            raise ValueError("Limit must be a NumPy 1-D array")

        if ndarray_contains_nan_inf(limit):
            raise ValueError("Limit contains NaN or inf values")

        if self._variables.has_variable_of_type(Vtype.BIPOLAR):
            raise ValueError("Cannot add equality constraint with variable vector set to 'bipolar'")

        self._constraints.add_constraint(
            constraint_weights=constraint_mask,
            constraint_bounds=np.repeat(limit, 2).reshape(-1, 2)
        )
        self._manifest.activate_equality_constraint()

    def add_equality_constraint(self, constraint_mask: np.ndarray, limit: np.float32) -> None:
        """
        Adds an equality constraint vector to the model.

        :param constraint_mask: The constraint_mask vector of shape (N,) where N is the number of variables.
        :type constraint_mask: a NumPy 1-D dense ndarray (float32)
        :param limit: Limit value to the constraint mask
        :type limit: np.float32

        :raise MissingVariableError: If no variable have been added to the model.
        :raises MaximumConstraintLimitError: The number of constraint exeed the limit.
        :raise ValueError: If the constraint_mask shape does not fit the expected shape of this model.
        :raise ValueError: If the constraint_mask or limit contains irregular format ('NaN' or 'inf')
        """
        if constraint_mask.ndim > 1:
            raise ValueError(
                "Cannot use add_equality_constraint() function with a matrix, " \
                "please use add_equality_constraint_matrix() insead")

        self.add_equality_constraints_matrix(reshape_to_2d(constraint_mask), np.full((1,), limit, dtype=np.float32))


    def add_inequality_constraints_matrix(self, constraint_mask: np.ndarray, constraint_bounds: np.ndarray):
        """
        Adds inequality constraint matrix to the model.

        :param constraint_mask: The constraint_mask vector of shape (M, N) where N is the number of variables.
        :type constraint_mask: A NumPy 2-D dense ndarray (float32)
        :param constraints_bounds: Vector of shape (M, 2) where M is the number of constraints
        :type constraint_bounds: A NumPy 2-D ndarray (float32)

        :raise MissingVariableError: If no variable have been added to the model.
        :raises MaximumConstraintLimitError: The number of constraint exeed the limit.
        :raise ValueError: If the constraint_mask shape does not fit the expected shape of this model.
        :raise ValueError: A lowerbound is equal or higher than its given upperbound
        :raise ValueError: If the constraint_mask contains irregular format ('NaN' or 'inf')
        """
        if self._variables.n_variables() == 0:
            raise MissingVariableError("Cannot set constraints before adding a variable to the model.")

        if constraint_mask.dtype != np.float32 or constraint_bounds.dtype != np.float32:
            raise ValueError(f"Input parameters must be float32, got Constraint mask: {constraint_mask.dtype}, Limit: {constraint_bounds.dtype}")

        if constraint_mask.ndim == 1:
            raise ValueError(
                "Cannot use add_inequality_constraint_matrix() function with a vector, " \
                "please use add_inequality_constraint() insead")

        if ndarray_contains_nan_inf(constraint_mask):
            raise ValueError("Constraint mask contains NaN  or inf values.")

        if is_upperbound_bigger_equal_lowerbound(constraint_bounds):
            raise ValueError("Constraint bounds contains lowerbounds equal or higher than their upperbound.")

        self._constraints.add_constraint(
            constraint_weights=constraint_mask,
            constraint_bounds=constraint_bounds
        )
        self._manifest.activate_inequality_constraint()


    def add_inequality_constraint(self, constraint_mask: np.ndarray, constraint_bounds: np.ndarray):
        """
        Adds inequality constraint vector to the model. At least one bound must be set.

        :param constraint_mask: The constraint_mask vector of shape (N,) where N is the number of variables.
        :type constraint_mask: A NumPy 1-D dense ndarray (float32)
        :param constraints_bounds: Vector of shape (2,)
        :type constraint_bounds: A NumPy 1-D ndarray (float32)

        :raise MissingVariableError: If no variable have been added to the model.
        :raises MaximumConstraintLimitError: The number of constraint exeed the limit.
        :raise ValueError: If the constraint_mask shape does not fit the expected shape of this model.
        :raise ValueError: If the constraint_mask contains irregular format ('NaN' or 'inf')
        :raise ValueError: Lowerbound is equal or higher than the upperbound
        """
        if constraint_mask.ndim > 1:
            raise ValueError(
                "Cannot use add_inequality_constraint() function with a matrix, " \
                "please use add_inequality_constraint_matrix() insead")

        self.add_inequality_constraints_matrix(reshape_to_2d(constraint_mask), reshape_to_2d(constraint_bounds))


    def optimize(self, *, beta=[0.1], coupling_mult=0.5, timeout_in_secs=10.0, num_chains=8, num_engines=1, normalized=False):
        """
        Optimize this model.

        Note: All of the files used during the computation will be cleaned at the end.

        :param beta: beta hyper parameter used by the backend solver.
        :param coupling_mult: coupling_mult hyper parameter used by the backend solver.
        :param timeout_in_secs: Maximum time (in seconds) the backend solver can take to resolve this problem.
        :param num_chains: num_chains hyper parameter used by the backend solver.
        :param num_engines: num_engines parameter used by the backend solver.
        :param normalized: normalized paramater used by backend solver.

        For more information on how to tunes those parameters, visit the API doc at `https://docs.titanq.infinityq.io/`

        :raise MissingVariableError: If no variable have been added to the model.
        :raise MissingObjectiveError: If no variable have been added to the model.

        Example
        ~~~~~~~
        ..  highlight:: python
        ..  code-block:: python
        # set up model, objective and variable
        ...

        # basic solve
        response = model.optimize(timeout_in_secs=60)

        # multiple engine
        response = model.optimize(timeout_in_secs=60, num_engines=2)

        # custom values
        response = model.optimize(beta=[0.1], coupling_mult=0.75, num_chains=8)

        # print values
        print("-" * 15, "+", "-" * 26, sep="")
        print("Ising energy   | Result vector")
        print("-" * 15, "+", "-" * 26, sep="")
        for ising_energy, result_vector in response.result_items():
            print(f"{ising_energy: <14f} | {result_vector}")
        """
        if self._variables.n_variables() == 0:
            raise MissingVariableError("Cannot optimize before adding a variable to the model.")

        if self._objective is None:
            raise MissingObjectiveError("Cannot optimize before adding an objective to the model.")

        result, metrics = self._solve(beta, coupling_mult, timeout_in_secs, num_chains, num_engines, normalized)

        return OptimizeResponse(self._variables, result, metrics)

    def _solve(self,
            beta: List[float],
            coupling_mult: float,
            timeout_in_secs: float,
            num_chains: int,
            num_engines: int,
            normalized: bool
        ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        issue a solve request and wait for it to complete.

        :param beta: beta hyper parameter used by the backend solver.
        :param coupling_mult: coupling_mult hyper parameter used by the backend solver.
        :param timeout_in_secs: Maximum time (in seconds) the backend solver can take to resolve this problem.
        :param num_chains: num_chains hyper parameter used by the backend solver.
        :param num_engines: num_engines parameter used by the backend solver.

        :return: the result numpy array and the metric json object
        """
        with self._storage_client.temp_files_manager(
            self._objective.bias(),
            self._objective.weights(),
            self._constraints.bounds() if self._constraints else None,
            self._constraints.weights() if self._constraints else None,
            # variables bounds is only sent if variable is set to binary
            self._variables.variable_bounds() if not self._variables.has_variable_of_type(Vtype.BIPOLAR) else None
        ) as temp_files:

            # api request
            request = api_model.SolveRequest(
                input=temp_files.input(),
                output=temp_files.output(),
                parameters=api_model.Parameters(
                    beta=beta,
                    coupling_mult=coupling_mult,
                    num_chains=num_chains,
                    num_engines=num_engines,
                    normalized=normalized,
                    timeout_in_secs=timeout_in_secs,
                    variable_types=self._variables.get_variable_types_str(self._manifest.has_equality_constraint(), self._manifest.has_inequality_constraint())
                )
            )

            # adding manifest flags to the request
            request.input.manifest = api_model.Manifest(
                has_set_partitioning_constraint=self._manifest.has_set_partitioning_constraint(),
                has_cardinality_constraint=self._manifest.has_cardinality_constraint(),
                has_equality_constraint=self._manifest.has_equality_constraint(),
                has_inequality_constraint=self._manifest.has_inequality_constraint()
            )

            solve_response = self._titanq_client.solve(request)

            # wait for result to be uploaded by the solver and download it
            archive_file_content = temp_files.download_result()
            with zipfile.ZipFile(io.BytesIO(archive_file_content), 'r') as zip_file:
                try:
                    metrics_content = zip_file.read("metrics.json")
                    result_content = zip_file.read("result.npy")
                except KeyError as ex:
                    try:
                        error_content = zip_file.read("error.json")
                        raise OptimizeError(json.loads(error_content)["error"]) from ex
                    except KeyError as e:
                        raise OptimizeError(
                            "Unexpected error in the solver, please contact InfinityQ support for more help" \
                            f" and provide the following computation id {solve_response.computation_id}") from e

        log.debug("Optimization completed")
        return np.load(io.BytesIO(result_content)), json.loads(metrics_content)
