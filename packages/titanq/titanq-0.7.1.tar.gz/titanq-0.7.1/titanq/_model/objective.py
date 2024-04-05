import enum
from typing import Tuple

import numpy as np


class Target(enum.Enum):
    MINIMIZE = 'minimize'


def _verify_nd_array(array: np.ndarray, array_name: str, *, expected_shape: Tuple, expected_type: np.dtype):
    """
    Make sure the given array is the right shape and the right type.

    :param array: The array to verify.
    :param array_name: the name of the array to be verified, use in error message.
    :param expected_shape: numpy compatible tuple of the expected shape.
    :param expected_type: expected numpy type for the array.

    :raise ValueError: if the array is not the right shape.
    :raise ValueError: if the value inside the array is not the right data type.
    """

    if array.shape != expected_shape:
        raise ValueError(f"{array_name} shape {array.shape} does not fit the shape of the variable previously defined. Expected: {expected_shape}.")

    if array.dtype != expected_type:
        raise ValueError(f"Unsupported {array_name} dtype ({array.dtype}). Expected: {expected_type}.")


class Objective:
    """
    Objective passed to TitanQ platform. It is consisted of the weight matrix and the bias vector.
    """

    def __init__(self, var_size: int, weights: np.ndarray, bias: np.ndarray, target=Target.MINIMIZE) -> None:
        _verify_nd_array(weights, "weights", expected_shape=(var_size, var_size), expected_type=np.float32)
        _verify_nd_array(bias, "bias", expected_shape=(var_size, ), expected_type=np.float32)

        self._weights = weights
        self._bias = bias
        self._target = target

    def weights(self) -> np.ndarray:
        """
        :return: The weights matrix of this objective.
        """
        return self._weights

    def bias(self) -> np.ndarray:
        """
        :return: The bias vector of this objective.
        """
        return self._bias

    def target(self) -> Target:
        """
        :return: The Target for this objective.
        """
        return self._target