import numpy as np

from titanq._model.variable import VariableVector, Vtype


def test_variable_types_as_list():
    variable_vector = VariableVector("x", 3, Vtype.BINARY)
    assert "bbb" == variable_vector.variable_types_as_list()


def test_create_variable_bounds():
    variable_vector = VariableVector("x", 3, Vtype.BINARY)
    assert (np.array([[0, 1], [0, 1], [0, 1]]) == variable_vector.create_variable_bounds()).all()