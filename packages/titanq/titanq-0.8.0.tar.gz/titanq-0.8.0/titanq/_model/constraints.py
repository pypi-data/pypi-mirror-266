import logging
import numpy as np
from numpy.typing import NDArray
from typing import Optional

from .errors import ConstraintSizeError, MaximumConstraintLimitError
from .numpy_util import convert_to_float32

log = logging.getLogger("TitanQ")

MAX_CONSTRAINTS_COUNT = 16_000

class Constraints:
    def __init__(self) -> None:
        self._variable_size = 0
        self._constraint_weights = None
        self._constraint_bounds = None


    def is_empty(self) -> bool :
        return self._constraint_bounds is None and self._constraint_weights is None


    def augment_size(self, size: int):
        self._variable_size += size


    def add_constraint(self, constraint_weights: np.ndarray, constraint_bounds: np.ndarray):
        """
        Add a constraint to the existing ones

        :param constraint_weights: constraint_weights to append to the existing ones.
        :param constraint_bounds: constraint_bounds to append to the existing ones.

        :raises ConstraintSizeError: constraint size is different than variable size.
        :raises MaximumConstraintLimitError: the number of constraint exeed the limit.
        """
        if constraint_weights.shape[1] != self._variable_size:
            raise ConstraintSizeError(
                "Constraint mask shape does not match the variable size. " \
                f"Constraint size: {constraint_weights.shape[1]}, Variable size: {self._variable_size}")

        if self._constraints_rows() + constraint_weights.shape[0] > MAX_CONSTRAINTS_COUNT:
            raise MaximumConstraintLimitError(
                "Cannot add additional constraints. The limit of constraints have been reached. " \
                f"Number of constraints: {self._constraints_rows()} while {self._constraints_rows() + constraint_weights.shape[0]} is trying to be added."
            )

        # API only takes np.float32
        constraint_weights = convert_to_float32(constraint_weights)
        constraint_bounds = convert_to_float32(constraint_bounds)

        self._append_constraint_weights(constraint_weights)
        self._append_constraint_bounds(constraint_bounds)


    def weights(self):
        """
        :return: The weights constraints.
        """
        return self._constraint_weights


    def bounds(self):
        """
        :return: The bounds constraints.
        """
        return self._constraint_bounds


    def _append_constraint_weights(self, constraint_weights_to_add: NDArray[np.float32]) -> None:
        """Appends ``constraint_weights_to_add`` to the existing one."""
        if self._constraint_weights is None:
            self._constraint_weights = constraint_weights_to_add
        else:
            self._constraint_weights = np.append(self._constraint_weights, constraint_weights_to_add, axis=0)


    def _append_constraint_bounds(self, constraint_bounds_to_add: NDArray[np.float32]) -> None:
        """Appends ``constraint_bounds_to_add`` to the existing one."""
        if self._constraint_bounds is None:
            self._constraint_bounds = constraint_bounds_to_add
        else:
            self._constraint_bounds =  np.append(self._constraint_bounds, constraint_bounds_to_add, axis=0)


    def _constraints_rows(self) -> int:
        """
        :return: The number of constraints (row) already set, 0 if never set
        """
        if self._constraint_weights is None:
            return 0
        return self._constraint_weights.shape[0]

    def set_constraint_matrices(
        self,
        constraint_weights: np.ndarray,
        constraint_bounds: np.ndarray
    ) -> None:
        """
        Overides add_constraint and manually set the constraint weights and the constraint bounds

        NOTE: Should be removed when equality and inequality constraints are added

        :param constraint_weights: already formed constraint weights
        :param constraint_bounds: already formed constraint bounds
        """
        weights_shape = constraint_weights.shape
        bounds_shape = constraint_bounds.shape

        # validate shapes
        if len(weights_shape) != 2:
            raise ValueError(f"constraint_weights should be a 2d matrix. Got something with shape: {weights_shape}")

        if len(bounds_shape) != 2:
            raise ValueError(f"constraint_bounds should be a 2d matrix. Got something with shape: {bounds_shape}")

        if weights_shape[1] != self._variable_size:
            raise ValueError(f"constraint_weights shape does not match variable size. Expected (M, {self._variable_size}) where M is the number of constraints")
        n_constraints = weights_shape[0]

        if n_constraints == 0:
            raise ValueError("Need at least 1 constraints")

        if bounds_shape[0] != n_constraints:
            raise ValueError(f"constraint_bounds shape does not match constraint_weights size. Expected ({n_constraints}, 2)")

        if bounds_shape[1] != 2:
            raise ValueError(f"constraint_bounds shape is expected to be ({n_constraints}, 2)")

        if constraint_weights.dtype != np.float32:
            raise ValueError(f"Weights constraints vector dtype should be np.float32")

        if constraint_bounds.dtype != np.float32:
            raise ValueError(f"Bounds constraints vector dtype should be np.float32")

        self._constraint_weights = constraint_weights
        self._constraint_bounds = constraint_bounds
