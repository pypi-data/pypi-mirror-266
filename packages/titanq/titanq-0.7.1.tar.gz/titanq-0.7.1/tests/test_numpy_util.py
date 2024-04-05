import pytest
import numpy as np
from titanq._model.numpy_util import (
    convert_to_float32,
    is_upperbound_bigger_equal_lowerbound,
    is_ndarray_binary,
    ndarray_contains_nan_inf,
    reshape_to_2d,
    validate_cardinalities,
)

@pytest.mark.parametrize("array, expected_dtype", [
    (np.array([[1, 2], [3, 4]]), np.float32),
    (np.array([[1.5, 2.5], [3.5, 4.5]]), np.float32),
    (np.empty((0, 0)), np.float32),
    (np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]]), np.float32)
])
def test_convert_to_float32(array: np.ndarray, expected_dtype: np.dtype):
    result = convert_to_float32(array)
    assert result.dtype == expected_dtype


@pytest.mark.parametrize("shape, expected_error", [
    ((4,), None),
    ((1,4), ValueError),
    ((99,), None),
    ((), AttributeError),
    ((99,0), ValueError),
    ((4, 4), ValueError),
    ((0,4), ValueError)
])
def test_reshape_to_2d(shape: np.shape, expected_error):
    reshaped_array = np.random.rand(*shape)

    if expected_error:
        with pytest.raises(expected_error):
            result = reshape_to_2d(reshaped_array)
    else:
        result = reshape_to_2d(reshaped_array)
        assert result.ndim == 2


@pytest.mark.parametrize("array, expected_result", [
    (np.array([2]), False),
    (np.array([2, 0]), False),
    (np.array([-1, 0]), False),
    (np.array([0, 1.01]), False),
    (np.array([[0, 0], [0, 2]]), False),
    (np.array([0]), True),
    (np.array([0, 1]), True),
    (np.array([[1, 1], [0, 0]]), True),
])
def test_is_ndarray_binary(array, expected_result):
    assert is_ndarray_binary(array) == expected_result


@pytest.mark.parametrize("array, expected_value", [
    (np.array([0]), False),
    (np.array([1]), False),
    (np.array([1.01]), False),
    (np.array([-1.01]), False),
    (np.array([np.nan]), True),
    (np.array([-np.nan]), True),
    (np.array([np.NaN]), True),
    (np.array([np.NAN]), True),
    (np.array([np.inf]), True),
    (np.array([-np.inf]), True),
])
def test_ndarray_contains_nan_inf(array, expected_value):
    assert ndarray_contains_nan_inf(array) == expected_value

@pytest.mark.parametrize("array, expected_value", [
    (np.array([[0, 1], [-1, 4000]]), False),
    (np.array([[1, 1], [0, 1]]), True),
    (np.array([[1.01, 1], [5.4, 1]]), True),
])
def test_is_upperbound_bigger_equal_lowerbound(array, expected_value):
    assert is_upperbound_bigger_equal_lowerbound(array) == expected_value


@pytest.mark.parametrize("cardinalities, expected_error", [
    (2, None),
    (3, None),
    (4, ValueError),
])
def test_validate_cardinalities(cardinalities, expected_error):
    if expected_error:
        with pytest.raises(expected_error):
            validate_cardinalities(np.array([[1,1,1]]), np.array([cardinalities]))
    else:
        validate_cardinalities(np.array([[1,1,1]]), np.array([cardinalities]))