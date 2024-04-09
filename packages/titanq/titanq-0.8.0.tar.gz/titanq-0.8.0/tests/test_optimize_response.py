import numpy as np

from titanq import OptimizeResponse
from titanq._model.variable_list import VariableVectorList
from titanq._model.variable import BinaryVariableVector

def test_multiple_variables():
    result = np.array([
        [0, 1, 1, 0, 1, 0],
        [1, 0, 0, 0, 0, 1],
    ], dtype=np.float32)
    variable_list = VariableVectorList()
    variable_list.add(BinaryVariableVector('x', 4))
    variable_list.add(BinaryVariableVector('y', 2))

    response = OptimizeResponse(variable_list, result, {})

    expected_x = np.array([
        [0, 1, 1, 0],
        [1, 0, 0, 0],
    ], dtype=np.float32)

    expected_y = np.array([
        [1, 0],
        [0, 1],
    ], dtype=np.float32)

    assert np.array_equal(response.x, expected_x)
    assert np.array_equal(response.y, expected_y)
    assert np.array_equal(response.result_vector(), result)


def test_get_metrics():
    metrics = { "computation_metrics": { "metrics1": 1, "metrics2": "value2" }}
    variable_list = VariableVectorList()
    variable_list.add(BinaryVariableVector('x', 6))
    response = OptimizeResponse(variable_list,  np.random.rand(2, 6).astype(np.float32), metrics)

    print(response.computation_metrics("metrics1"))

    assert response.computation_metrics("metrics1") == metrics["computation_metrics"]["metrics1"]
    assert response.computation_metrics("metrics2") == metrics["computation_metrics"]["metrics2"]
