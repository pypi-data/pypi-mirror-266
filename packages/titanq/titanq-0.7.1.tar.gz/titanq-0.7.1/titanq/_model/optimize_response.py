import logging
from typing import Any, Dict, List, Tuple, Union
import uuid
import warnings

import numpy as np

log = logging.getLogger('TitanQ')

class OptimizeResponse:
    """
    Object containing Optimization response and all its metrics.
    """
    def __init__(self, var_name: str, result_array: np.ndarray, metrics: Dict[str, Any]) -> None:
        self._var_name = var_name
        self._result_vector = result_array
        self._metrics = metrics


    def __getattr__(self, attr: str):
        # if attribute is the _var_name
        if attr == self._var_name:
            return self.result_vector()

        # This is to keep compatibility with older version of SDK
        if attr == "ising_energy":
            try:
                return self.__getattr__("solutions_objective_value")
            except (AttributeError, KeyError):
                pass


        warnings.warn(
            'Obtaining metrics directly as an attribute is deprecated. Use computation_metrics() or original_input_params() instead.',
            DeprecationWarning,
            stacklevel=2
        )


        # check inside computation metrics and original params for the attribute
        try:
            return self.computation_metrics(attr)
        except KeyError:
            pass

        try:
            return self.original_input_params(attr)
        except KeyError:
            pass

        # was not found, try the older behavior
        try:
            return self._metrics[attr]
        except KeyError:
            raise AttributeError(attr)


    def result_vector(self) -> np.ndarray:
        """
        :return: The result vector of this optimization.
        """
        return self._result_vector


    def result_items(self) -> List[Tuple[int, np.ndarray]]:
        """
        ex. [(-10000, [0, 1, 1, 0]), (-20000, [1, 0, 1, 0]), ...]

        :return: list of tuples containing the solutions objective value and it's corresponding result vector
        """

        solutions_objective_value = self.ising_energy
        return [(solutions_objective_value[i], self._result_vector[i]) for i in range(len(self._result_vector))]


    def computation_metrics(self, key: str = None) -> Any:
        """
        :return: All computation metrics if no key is given of the specific metrics with the associated key if one is provided.

        :raise KeyError: The given key does not exist
        """
        metrics = self._metrics['computation_metrics']
        if key:
            metrics = metrics[key]
        return metrics


    def computation_id(self) -> uuid.UUID:
        """
        The computation id is a Universal unique id that identify this computation inside the TitanQ platform.

        Provide this id on any support request to the InfinityQ.

        :return: The computation id of this solve.
        """
        return self._metrics['computation_id']


    def original_input_params(self, key: str = None) -> Any:
        """
        :return: All original params if no key is given of the specific params with the associated key if one is provided.

        :raise KeyError: The given key does not exist
        """
        metrics = self._metrics['original_input_params']
        if key:
            metrics = metrics[key]
        return metrics


    def metrics(self, key: str = None) -> Union[str, Dict[str, Any]]:
        """
        # Deprecated
        use computation_metrics() or original_input_params instead

        :return: All metrics if no key is given of the specific metrics with the associated key if one is provided.

        :raise KeyError: The given key does not exist
        """
        warnings.warn(
            'Calling metrics() is deprecated. Use computation_metrics or original_input_params instead.',
            DeprecationWarning,
            stacklevel=2
        )
        if key:
            return self._metrics[key]
        else:
            return self._metrics
