import logging
import numpy as np
from numpy.typing import NDArray

log = logging.getLogger("TitanQ")


def convert_to_float32(array: np.ndarray) -> NDArray[np.float32]:
    """
    Changes a given array type to np.NDArray[np.float32].

    :param array: input constraint mask of shape (M, N).
    :type array: a NumPy 2-D dense ndarray.

    :return: Array of type float32
    :rtype: NDArray[np.float32]
    """
    return array.astype(np.float32)


def reshape_to_2d(array: np.ndarray) -> np.ndarray:
    """
    Reshape a given array to a 2-D array.

    :param array: input constraint mask of shape (N,).
    :type array: a NumPy 1-D dense ndarray.

    :return: Array of type Any
    :rtype: NDArray[np.Any]
    """
    if array.ndim != 1:
        raise ValueError("Input array is not 1-D. Cannot reshape array.")
    return array.reshape(1, -1)


def is_ndarray_binary(array: np.ndarray) -> bool:
    """
    :return: if all values ares either 1 or 0 (binary)
    """
    return np.all((array == 1) | (array == 0))


def ndarray_contains_nan_inf(array: np.ndarray) -> bool:
    """
    :return: if the array contains NaN or inf type
    """
    return np.isnan(array).any() or np.isinf(array).any()

def is_upperbound_bigger_equal_lowerbound(array: np.ndarray) -> bool:
    """
    finds lowerbounds larger or equal than upperbounds in NumPy 2-D Array (M, 2)
    where M is the number of rows

    :return: if each value of the left side is lower lower than the right side
    """
    left_slice = array[:, 0]
    right_slice = array[:, 1]

    equal_or_higher = np.where(left_slice >= right_slice)[0]
    return len(equal_or_higher) > 0

def validate_cardinalities(constraint_mask: np.ndarray, cardinalities: np.ndarray) -> None:
    """
    Validates each row's sum of a binary array against corresponding values in a cardinalities array.
    It prints warnings if the sum is equal to the cardinality and raises an error if the sum is less than the cardinality.

    :param array: input constraint mask of shape (M, N).
    :type array: a NumPy 2-D dense ndarray.

    :param cardinalities: The constraint_rhs vector of shape (M,) where M is the number of constraints.
    :type cardinalities:  a NumPy 1-D ndarray.
    """
    binary_sums = np.sum(constraint_mask, axis=1)

    equal_indices = np.where(binary_sums == cardinalities[0])[0]
    less_indices = np.where(binary_sums < cardinalities)[0]

    if equal_indices.size > 0:
        log.warning(f" The sum of rows {', '.join(map(str, equal_indices))} in the binary array equals its corresponding cardinality.")

    if less_indices.size > 0:
        raise ValueError(f"The sum of rows {', '.join(map(str, less_indices))} in the binary array is less than its corresponding cardinality.")