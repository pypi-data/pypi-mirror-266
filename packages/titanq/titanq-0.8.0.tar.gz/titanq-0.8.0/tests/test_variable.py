import numpy as np
import pytest

from titanq._model.variable import BinaryVariableVector, BipolarVariableVector, IntegerVariableVector, Vtype


@pytest.mark.parametrize("variable_vector, expected",  [
    (BinaryVariableVector('x', 3), Vtype.BINARY),
    (BipolarVariableVector('x', 3), Vtype.BIPOLAR),
    (IntegerVariableVector('x', 3, [(1, 2)] * 3), Vtype.INTEGER),
])
def test_variable_types(variable_vector, expected):
    assert variable_vector.vtype() == expected


@pytest.mark.parametrize("variable_vector, expected",  [
    (BinaryVariableVector('x', 3), "bbb"),
    (IntegerVariableVector('x', 4, [(1, 2)] * 4), "iiii"),
])
def test_variable_types_as_list(variable_vector, expected):
    assert variable_vector.variable_types_as_list() == expected


def test_binary_variable_bounds():
    variable_vector = BinaryVariableVector("x", 3)
    assert (np.array([[0, 1], [0, 1], [0, 1]]) == variable_vector.variable_bounds()).all()

