import datetime
import io
import json
import uuid
import numpy as np
import pytest
from typing import Any, Dict, List
import zipfile

from titanq import Model, Vtype, errors, Target
from titanq._storage.s3_storage import S3Storage
from titanq._storage.managed_storage import ManagedStorage
from titanq._client.model import SolveResponse

from .mock import TitanQClientMock, MockS3StorageClient


def file_in_filename_list(filename: str, filename_list: List[str]) -> bool:
    return any(filename in s for s in filename_list)

def np_array_to_bytes(arr: np.ndarray) -> bytes:
    buf = io.BytesIO()
    np.save(buf, arr)
    return buf.getvalue()

@pytest.fixture
def mock_metrics() -> Dict[str, Any]:
    return {
        "computation_metrics": {
            "metrics1": 1,
            "metrics2": "value2"
        }
    }

@pytest.fixture
def mock_result() -> Dict[str, Any]:
    return [np.random.rand(10).astype(np.float32) for _ in range(10)]

@pytest.fixture
def mock_s3_storage(mock_metrics, mock_result) -> MockS3StorageClient:
    # expected npy result file content
    expected_result_buffer = io.BytesIO()
    np.save(expected_result_buffer, mock_result)

    # set mock client with mock values
    buff = io.BytesIO()
    with zipfile.ZipFile(buff, 'w') as file:
        file.writestr("result.npy", expected_result_buffer.getvalue())
        file.writestr("metrics.json", json.dumps(mock_metrics).encode())

    return MockS3StorageClient(buff.getvalue())

@pytest.fixture
def mock_titanq_client() -> TitanQClientMock:
    return TitanQClientMock(solve_response=SolveResponse(
        computation_id=str(uuid.uuid4()),
        status="queued",
        message="Computation have been queued"
    ))

@pytest.fixture
def model_s3_client(mock_s3_storage, mock_titanq_client) -> Model:
    model = Model(
        api_key="test_api_key",
        storage_client=mock_s3_storage
    )

    model._titanq_client = mock_titanq_client
    return model


@pytest.fixture
def constant_datetime(monkeypatch):
    constant_datetime = datetime.datetime(2024,1,1,8,0,0)
    class MockDatetime(datetime.datetime):
        @classmethod
        def now(cls):
            return constant_datetime

    monkeypatch.setattr(datetime, 'datetime', MockDatetime)
    return constant_datetime

@pytest.mark.parametrize("api_key, storage_client ,expected_storage_class", [
    ("api_key", S3Storage(access_key="aws_access_key", secret_key="aws_secret_access_key", bucket_name="bucket_name"), S3Storage),
    ("api_key", ManagedStorage(TitanQClientMock()), ManagedStorage),
])
def test_selected_storage(api_key, storage_client, expected_storage_class):
    model = Model(api_key=api_key, storage_client=storage_client)
    assert isinstance(model._storage_client, expected_storage_class)


@pytest.mark.parametrize("name, size, vtype, error", [
    ('x', 1, Vtype.BINARY, None),
    ('x', 47, Vtype.BINARY, None),
    ('x', -1, Vtype.BINARY, ValueError),
    ('x', 0, Vtype.BINARY, ValueError)
])
def test_new_variable(model_s3_client, name, size, vtype, error):
    if error:
        with pytest.raises(error):
            model_s3_client.add_variable_vector(name, size, vtype)
    else:
        model_s3_client.add_variable_vector(name, size, vtype)


@pytest.mark.parametrize("weights_shape, bias_shape, objective, error", [
    ((10, 10), (10,), Target.MINIMIZE, None),
    ((11, 10), (10,), Target.MINIMIZE, ValueError),
    ((10, 11), (10,), Target.MINIMIZE, ValueError),
    ((11, 11), (10,), Target.MINIMIZE, ValueError),
    ((10, 10, 10), (10,), Target.MINIMIZE, ValueError),
    ((10,), (10,), Target.MINIMIZE, ValueError),
    ((10,10), (9,), Target.MINIMIZE, ValueError),
    ((10,10), (10,1), Target.MINIMIZE, ValueError),
    ((10,10), (10,2), Target.MINIMIZE, ValueError),
])
def test_set_objective(model_s3_client, weights_shape, bias_shape, objective, error):
    model_s3_client.add_variable_vector('x', 10, Vtype.BINARY)

    weights = np.random.rand(*weights_shape).astype(np.float32)
    bias = np.random.rand(*bias_shape).astype(np.float32)

    if error:
        with pytest.raises(error):
            model_s3_client.set_objective_matrices(weights, bias, objective)
    else:
        model_s3_client.set_objective_matrices(weights, bias, objective)

@pytest.mark.parametrize("weights_data_type, bias_data_type, error", [
    (np.float32, np.float32, None),
    (np.float64, np.float32, ValueError),
    (np.float32, np.float64, ValueError),
    (np.int32, np.float32, ValueError),
    (np.float32, np.int32, ValueError),
    (np.bool_, np.float32, ValueError),
    (np.float32, np.bool_, ValueError),
    (np.byte, np.float32, ValueError),
    (np.float32, np.byte, ValueError),
    (np.short, np.float32, ValueError),
    (np.float32, np.short, ValueError),
])
def test_objective_matrices_data_type(model_s3_client, weights_data_type, bias_data_type, error):
    model_s3_client.add_variable_vector('x', 10, Vtype.BINARY)

    weights = np.random.rand(10, 10).astype(weights_data_type)
    bias = np.random.rand(10).astype(bias_data_type)

    if error:
        with pytest.raises(error):
            model_s3_client.set_objective_matrices(weights, bias, Target.MINIMIZE)
    else:
        model_s3_client.set_objective_matrices(weights, bias, Target.MINIMIZE)


def test_set_objective_without_variable(model_s3_client):
    weights = np.random.rand(10, 10)
    bias = np.random.rand(10)

    with pytest.raises(errors.MissingVariableError):
        model_s3_client.set_objective_matrices(weights, bias, Target.MINIMIZE)


def test_set_2_objective(model_s3_client):
    model_s3_client.add_variable_vector('x', 10, Vtype.BINARY)

    weights = np.random.rand(10, 10).astype(np.float32)
    bias = np.random.rand(10).astype(np.float32)

    model_s3_client.set_objective_matrices(weights, bias, Target.MINIMIZE)

    with pytest.raises(errors.ObjectiveAlreadySetError):
        model_s3_client.set_objective_matrices(weights, bias, Target.MINIMIZE)


def test_optimize_no_variable(model_s3_client):
    with pytest.raises(errors.MissingVariableError):
        model_s3_client.optimize()


def test_optimize_no_objective(model_s3_client):
    model_s3_client.add_variable_vector('x', 10, Vtype.BINARY)

    with pytest.raises(errors.MissingObjectiveError):
        model_s3_client.optimize()


def test_optimize_no_constraints(model_s3_client, mock_s3_storage, mock_metrics, mock_result):
    model = model_s3_client

    # optimize using sdk
    weights = np.random.rand(10, 10).astype(np.float32)
    bias = np.random.rand(10).astype(np.float32)

    model.add_variable_vector('x', 10, Vtype.BINARY)
    model.set_objective_matrices(weights, bias)
    response = model.optimize()

    assert response.computation_metrics() == mock_metrics["computation_metrics"]
    assert (response.result_vector() == mock_result).all()

    assert mock_s3_storage.array_uploaded['bias'] == np_array_to_bytes(bias)
    assert mock_s3_storage.array_uploaded['weights'] == np_array_to_bytes(weights)
    assert mock_s3_storage.array_uploaded['constraint_weights'] == None
    assert mock_s3_storage.array_uploaded['constraint_bounds'] == None

    assert mock_s3_storage.file_removed


def test_optimize_with_set_constraints_matrices(model_s3_client, mock_s3_storage, mock_metrics, mock_result):
    model = model_s3_client

    # optimize using sdk
    weights = np.random.rand(10, 10).astype(np.float32)
    constraint_weights = np.random.rand(4, 10).astype(np.float32)
    bias = np.random.rand(10).astype(np.float32)
    constraint_bounds = np.random.rand(4, 2).astype(np.float32)

    model.add_variable_vector('x', 10, Vtype.BINARY)
    model.set_objective_matrices(weights, bias)
    model.set_constraints_matrices(constraint_weights, constraint_bounds)
    response = model.optimize()

    assert response.computation_metrics() == mock_metrics["computation_metrics"]
    assert (response.result_vector() == mock_result).all()

    assert mock_s3_storage.array_uploaded['bias'] == np_array_to_bytes(bias)
    assert mock_s3_storage.array_uploaded['weights'] == np_array_to_bytes(weights)
    assert mock_s3_storage.array_uploaded['constraint_weights'] == np_array_to_bytes(constraint_weights)
    assert mock_s3_storage.array_uploaded['constraint_bounds'] == np_array_to_bytes(constraint_bounds)

    assert mock_s3_storage.file_removed


@pytest.mark.parametrize("constraint_weights_shape, constraint_bounds_shape, error", [
    ((2, 10), (2,2), None),
    ((10, 10), (10,2), None),
    ((2, 10), (3,2), ValueError),
    ((2, 10), (2,), ValueError),
    ((2, 10), (10,2), ValueError),
    ((10, 2), (2,2), ValueError),
    ((10, ), (1,2), ValueError),
    ((2, 10), (3,2), ValueError),
    ((2, 11), (2,2), ValueError),
    ((0, 10), (0,2), ValueError),
])
def test_set_constraints(model_s3_client, constraint_weights_shape, constraint_bounds_shape, error):
    model_s3_client.add_variable_vector('x', 10, Vtype.BINARY)

    constraint_weights = np.random.rand(*constraint_weights_shape).astype(np.float32)
    constraint_bounds = np.random.rand(*constraint_bounds_shape).astype(np.float32)

    if error:
        with pytest.raises(error):
            model_s3_client.set_constraints_matrices(constraint_weights, constraint_bounds)
    else:
        model_s3_client.set_constraints_matrices(constraint_weights, constraint_bounds)


@pytest.mark.parametrize("vtype", [
    (Vtype.BINARY),
    (Vtype.BIPOLAR),
])
def test_vtype_sent(model_s3_client, mock_titanq_client, vtype):
    model = model_s3_client
    mock_client = mock_titanq_client

    # optimize using sdk
    weights = np.random.rand(10, 10).astype(np.float32)
    bias = np.random.rand(10).astype(np.float32)

    model.add_variable_vector('x', 10, vtype)
    model.set_objective_matrices(weights, bias)

    model.optimize()

    assert mock_client.request_sent.parameters.variable_types == str(vtype)


@pytest.mark.parametrize("constraint_weights_dtype, constraint_bounds_dtype, error", [
    (np.float32, np.float32, None),
    (np.float64, np.float32, ValueError),
    (np.float32, np.float64, ValueError),
    (np.int32, np.int32, ValueError),
])
def test_constraints_dtype(model_s3_client, constraint_weights_dtype, constraint_bounds_dtype, error):
    model_s3_client.add_variable_vector('x', 10, Vtype.BINARY)

    constraint_weights = np.random.rand(2, 10).astype(constraint_weights_dtype)
    constraint_bounds = np.random.rand(2, 2).astype(constraint_bounds_dtype)

    if error:
        with pytest.raises(error):
            model_s3_client.set_constraints_matrices(constraint_weights, constraint_bounds)
    else:
        model_s3_client.set_constraints_matrices(constraint_weights, constraint_bounds)



def test_constraints_without_variable(model_s3_client):
    constraint_weights = np.random.rand(2, 10).astype(np.float32)
    constraint_bounds = np.random.rand(2).astype(np.float32)

    with pytest.raises(errors.MissingVariableError):
        model_s3_client.set_constraints_matrices(constraint_weights, constraint_bounds)

    with pytest.raises(errors.MissingVariableError):
        model_s3_client.add_set_partitioning_constraints_matrix(np.array([[0, 0, 1, 0], [0, 1, 0, 0]]))

    with pytest.raises(errors.MissingVariableError):
        model_s3_client.add_set_partitioning_constraint(np.array([0, 1]))

    with pytest.raises(errors.MissingVariableError):
        model_s3_client.add_cardinality_constraints_matrix(np.array([[1, 0, 1, 0], [0, 1, 1, 1]]), np.array([2, 3]))

    with pytest.raises(errors.MissingVariableError):
        model_s3_client.add_cardinality_constraint(np.array([1, 1]), 2)


def test_add_set_partitioning_constraints_matrix(model_s3_client):
    model_s3_client.add_variable_vector('x', 4, Vtype.BINARY)

    model_s3_client.add_set_partitioning_constraints_matrix(np.array([[0, 0, 1, 0], [0, 1, 0, 0]]))
    np.testing.assert_equal(model_s3_client._constraints.weights(), np.array([[0, 0, 1, 0], [0, 1, 0, 0]]))
    np.testing.assert_equal(model_s3_client._constraints.bounds(), np.array([[1, 1], [1, 1]]))

    model_s3_client.add_set_partitioning_constraints_matrix(np.array([[0, 1, 0, 0], [1, 0, 0, 0]]))
    np.testing.assert_equal(model_s3_client._constraints.weights(), np.array([[0, 0, 1, 0], [0, 1, 0, 0], [0, 1, 0, 0], [1, 0, 0, 0]]))
    np.testing.assert_equal(model_s3_client._constraints.bounds(), np.array([[1, 1], [1, 1], [1, 1], [1, 1]]))


def test_add_set_partitioning_constraint(model_s3_client):
    model_s3_client.add_variable_vector('x', 2, Vtype.BINARY)

    model_s3_client.add_set_partitioning_constraint(np.array([0, 1]))
    np.testing.assert_equal(model_s3_client._constraints.weights(), np.array([[0, 1]]))
    np.testing.assert_equal(model_s3_client._constraints.bounds(), np.array([[1, 1]]))

    model_s3_client.add_set_partitioning_constraint(np.array([1, 0]))
    np.testing.assert_equal(model_s3_client._constraints.weights(), np.array([[0, 1], [1, 0]]))
    np.testing.assert_equal(model_s3_client._constraints.bounds(), np.array([[1, 1], [1, 1]]))


def test_add_cardinality_constraints_matrix(model_s3_client):
    model_s3_client.add_variable_vector('x', 4, Vtype.BINARY)

    model_s3_client.add_cardinality_constraints_matrix(np.array([[1, 0, 1, 0], [0, 1, 1, 1]]), np.array([2, 3]))
    np.testing.assert_equal(model_s3_client._constraints.weights(), np.array([[1, 0, 1, 0], [0, 1, 1, 1]]))
    np.testing.assert_equal(model_s3_client._constraints.bounds(), np.array([[2, 2], [3, 3]]))

    model_s3_client.add_cardinality_constraints_matrix(np.array([[0, 1, 0, 0], [1, 0, 0, 0]]), np.array([1, 1]))
    np.testing.assert_equal(model_s3_client._constraints.weights(), np.array([[1, 0, 1, 0], [0, 1, 1, 1], [0, 1, 0, 0], [1, 0, 0, 0]]))
    np.testing.assert_equal(model_s3_client._constraints.bounds(), np.array([[2, 2], [3, 3], [1, 1], [1, 1]]))

def test_add_cardinality_constraint(model_s3_client):
    model_s3_client.add_variable_vector('x', 2, Vtype.BINARY)

    model_s3_client.add_cardinality_constraint(np.array([1, 1]), 2)
    np.testing.assert_equal(model_s3_client._constraints.weights(), np.array([[1, 1]]))
    np.testing.assert_equal(model_s3_client._constraints.bounds(), np.array([[2, 2]]))

    model_s3_client.add_cardinality_constraint(np.array([0, 1]), 1)
    np.testing.assert_equal(model_s3_client._constraints.weights(), np.array([[1, 1], [0, 1]]))
    np.testing.assert_equal(model_s3_client._constraints.bounds(), np.array([[2, 2], [1, 1]]))

@pytest.mark.parametrize("constraint_mask, cardinality, error", [
    (np.array([1, 1]), 1, None),
    (np.array([1, 1]), 2, None),
    (np.array([1, 1]), 3, ValueError),
])
def test_cardinalities_sum(model_s3_client, constraint_mask, cardinality, error):
    model_s3_client.add_variable_vector('x', 2, Vtype.BINARY)

    if error:
        with pytest.raises(ValueError):
            model_s3_client.add_cardinality_constraint(constraint_mask, cardinality)
    else:
        model_s3_client.add_cardinality_constraint(constraint_mask, cardinality)

def test_cardinality_or_set_partitioning_constraint_variable_types(model_s3_client, mock_titanq_client):
    weights = np.random.rand(2, 2).astype(np.float32)
    bias = np.random.rand(2).astype(np.float32)

    model_s3_client.add_variable_vector('x', 2, Vtype.BINARY)
    model_s3_client.set_objective_matrices(weights, bias)
    model_s3_client.add_cardinality_constraint(np.array([1, 1]), 2)

    model_s3_client.optimize()

    assert mock_titanq_client.request_sent.parameters.variable_types == "binary"
    assert mock_titanq_client.request_sent.input.variable_bounds_file_name == 'test-variable_bounds.npy'

def test_add_equality_constraint(model_s3_client):
    model_s3_client.add_variable_vector('x', 2, Vtype.BINARY)

    model_s3_client.add_equality_constraint(np.array([1.05, -1.1], dtype=np.float32), -3.45)
    np.testing.assert_equal(model_s3_client._constraints.weights(), np.array([[1.05, -1.1]], dtype=np.float32))
    np.testing.assert_equal(model_s3_client._constraints.bounds(), np.array([[-3.45, -3.45]], dtype=np.float32))

    model_s3_client.add_equality_constraint(np.array([14, 0], dtype=np.float32), 0)
    np.testing.assert_equal(model_s3_client._constraints.weights(), np.array([[1.05, -1.1], [14, 0]], dtype=np.float32))
    np.testing.assert_equal(model_s3_client._constraints.bounds(), np.array([[-3.45, -3.45], [0, 0]], dtype=np.float32))


@pytest.mark.parametrize("method, kwargs", [
    ("add_set_partitioning_constraints_matrix", { "constraint_mask": np.array([[0,1]])}),
    ("add_set_partitioning_constraint",         { "constraint_mask": np.array([0,1])}),
    ("add_cardinality_constraints_matrix",      { "constraint_mask": np.array([[0,1]]),                   "cardinalities": np.array([1])}),
    ("add_cardinality_constraint",              { "constraint_mask": np.array([0,1]),                     "cardinality": 1 }),
    ("add_equality_constraints_matrix",         { "constraint_mask": np.array([[0,1]], dtype=np.float32), "limit": np.array([1], dtype=np.float32) }),
    ("add_equality_constraint",                 { "constraint_mask": np.array([0,1], dtype=np.float32),   "limit": 1 }),
    ("add_inequality_constraints_matrix",       { "constraint_mask": np.array([[0,1]], dtype=np.float32), "constraint_bounds": np.array([[-50, np.nan]], dtype=np.float32)}),
    ("add_inequality_constraint",               { "constraint_mask": np.array([0,1], dtype=np.float32),   "constraint_bounds": np.array([-50, np.nan], dtype=np.float32)}),
])
def test_constraint_weights_and_bounds_float_32_output(model_s3_client, method, kwargs):
    model_s3_client.add_variable_vector('x', 2, Vtype.BINARY)

    constraint_function = getattr(model_s3_client, method)
    constraint_function(**kwargs)

    assert model_s3_client._constraints.bounds().dtype == np.float32


def test_add_equality_constraint_matrix(model_s3_client):
    model_s3_client.add_variable_vector('x', 4, Vtype.BINARY)

    model_s3_client.add_equality_constraints_matrix(np.array([[-3.51, 0, 0, 0], [10, 0, 0, 0]], dtype=np.float32), np.array([2, 10], dtype=np.float32))
    np.testing.assert_equal(model_s3_client._constraints.weights(), np.array([[-3.51, 0, 0, 0], [10, 0, 0, 0]], dtype=np.float32))
    np.testing.assert_equal(model_s3_client._constraints.bounds(), np.array([[2, 2], [10, 10]], dtype=np.float32))

    model_s3_client.add_equality_constraints_matrix(np.array([[0, 5, 0, 0], [0, 0, -5, 0]], dtype=np.float32), np.array([-1, 1], dtype=np.float32))
    np.testing.assert_equal(model_s3_client._constraints.weights(), np.array([[-3.51, 0, 0, 0], [10, 0, 0, 0], [0, 5, 0, 0], [0, 0, -5, 0]], dtype=np.float32))
    np.testing.assert_equal(model_s3_client._constraints.bounds(), np.array([[2, 2], [10, 10], [-1, -1], [1, 1]], dtype=np.float32))

    with pytest.raises(ValueError):
        model_s3_client.add_equality_constraints_matrix(np.array([[1, 2, 3, 4]], dtype=np.float32), np.array([[10, 10]], dtype=np.float32))

    with pytest.raises(ValueError):
        model_s3_client.add_equality_constraints_matrix(np.array([[1, 2, 3, 4]], dtype=np.float32), np.array([10], dtype=np.int32))


def test_equality_constraint_override_variable_types(model_s3_client, mock_titanq_client):
    weights = np.random.rand(2, 2).astype(np.float32)
    bias = np.random.rand(2).astype(np.float32)

    model_s3_client.add_variable_vector('x', 2, Vtype.BINARY)
    model_s3_client.set_objective_matrices(weights, bias)
    model_s3_client.add_equality_constraint(np.array([1.05, -1.1], dtype=np.float32), -3.45)
    model_s3_client.optimize()

    assert mock_titanq_client.request_sent.parameters.variable_types == "bb"
    assert mock_titanq_client.request_sent.input.variable_bounds_file_name == "test-variable_bounds.npy"


def test_add_inequality_constraint(model_s3_client):
    model_s3_client.add_variable_vector('x', 2, Vtype.BINARY)

    model_s3_client.add_inequality_constraint(np.array([1.05, -1.1], dtype=np.float32), np.array([np.nan, -3.45], dtype=np.float32))
    np.testing.assert_equal(model_s3_client._constraints.weights(), np.array([[1.05, -1.1]], dtype=np.float32))
    np.testing.assert_equal(model_s3_client._constraints.bounds(), np.array([[np.nan, -3.45]], dtype=np.float32))

    model_s3_client.add_inequality_constraint(np.array([14, 0], dtype=np.float32), np.array([-0.09, 0], dtype=np.float32))
    np.testing.assert_equal(model_s3_client._constraints.weights(), np.array([[1.05, -1.1], [14, 0]], dtype=np.float32))
    np.testing.assert_equal(model_s3_client._constraints.bounds(), np.array([[np.nan, -3.45], [-0.09, 0]], dtype=np.float32))

    model_s3_client.add_inequality_constraint(np.array([76, -4.8], dtype=np.float32), np.array([None, -8], dtype=np.float32))
    np.testing.assert_equal(model_s3_client._constraints.weights(), np.array([[1.05, -1.1], [14, 0], [76, -4.8]], dtype=np.float32))
    np.testing.assert_equal(model_s3_client._constraints.bounds(), np.array([[np.nan, -3.45], [-0.09, 0], [None, -8]], dtype=np.float32))

def test_add_inequality_constraint_matrix(model_s3_client):
    model_s3_client.add_variable_vector('x', 2, Vtype.BINARY)
    model_s3_client.add_inequality_constraints_matrix(np.array([[-3.51, 0], [10, 0]], dtype=np.float32), np.array([[8, 9], [np.nan, 100_000]], dtype=np.float32))

    np.testing.assert_equal(model_s3_client._constraints.weights(), np.array([[-3.51, 0], [10, 0]], dtype=np.float32))
    np.testing.assert_equal(model_s3_client._constraints.bounds(), np.array([[8, 9], [np.nan, 100_000]], dtype=np.float32))

    with pytest.raises(ValueError):
        model_s3_client.add_equality_constraints_matrix(np.array([[1, 2]], dtype=np.float32), np.array([[np.nan, 10]], dtype=np.float32))

    with pytest.raises(ValueError):
        model_s3_client.add_equality_constraints_matrix(np.array([[1, 2]], dtype=np.float32), np.array([np.nan, 10], dtype=np.int32))

def test_inequality_constraint_override_variable_types(model_s3_client, mock_titanq_client):
    weights = np.random.rand(2, 2).astype(np.float32)
    bias = np.random.rand(2).astype(np.float32)

    model_s3_client.add_variable_vector('x', 2, Vtype.BINARY)
    model_s3_client.set_objective_matrices(weights, bias)
    model_s3_client.add_inequality_constraint(np.array([1.05, -1.1], dtype=np.float32), np.array([1.0, np.nan], dtype=np.float32))
    model_s3_client.optimize()

    assert mock_titanq_client.request_sent.parameters.variable_types == "bb"
    assert mock_titanq_client.request_sent.input.variable_bounds_file_name == "test-variable_bounds.npy"


def test_combination_constraint(model_s3_client):
    model_s3_client.add_variable_vector('x', 4, Vtype.BINARY)

    model_s3_client.add_set_partitioning_constraints_matrix(np.array([[0, 0, 1, 0], [0, 1, 0, 0]]))
    np.testing.assert_equal(model_s3_client._constraints.weights(), np.array([[0, 0, 1, 0], [0, 1, 0, 0]]))
    np.testing.assert_equal(model_s3_client._constraints.bounds(), np.array([[1, 1], [1, 1]]))

    model_s3_client.add_set_partitioning_constraint(np.array([0, 1, 0, 0]))
    np.testing.assert_equal(model_s3_client._constraints.weights(), np.array([[0, 0, 1, 0], [0, 1, 0, 0], [0, 1, 0, 0]]))
    np.testing.assert_equal(model_s3_client._constraints.bounds(), np.array([[1, 1], [1, 1], [1, 1]]))

    model_s3_client.add_cardinality_constraint(np.array([1, 1, 1, 1]), 2)
    np.testing.assert_equal(model_s3_client._constraints.weights(), np.array([[0, 0, 1, 0], [0, 1, 0, 0], [0, 1, 0, 0], [1, 1, 1, 1]]))
    np.testing.assert_equal(model_s3_client._constraints.bounds(), np.array([[1, 1], [1, 1], [1, 1], [2, 2]]))


@pytest.mark.parametrize("nmb_of_constraints, expected_error", [
    (15_999, None),
    (16_000, None),
    (16_001, errors.MaximumConstraintLimitError),
])
def test_number_of_constraints_threshold(model_s3_client, nmb_of_constraints, expected_error):
    i = 0
    model_s3_client.add_variable_vector('y', 2, Vtype.BINARY)

    if expected_error:
        with pytest.raises(expected_error):
            while (i < nmb_of_constraints):
                model_s3_client.add_set_partitioning_constraint(np.array([0, 1]))
                i += 1
    else:
        while (i < nmb_of_constraints):
            model_s3_client.add_set_partitioning_constraint(np.array([0, 1]))
            i += 1


def test_manifest(model_s3_client, mock_titanq_client):
    weights = np.random.rand(4, 4).astype(np.float32)
    bias = np.random.rand(4).astype(np.float32)

    # Construct the request
    model_s3_client.add_variable_vector('x', 4, Vtype.BINARY)
    model_s3_client.set_objective_matrices(weights, bias)

    model_s3_client.add_set_partitioning_constraint(np.array([0, 0, 1, 0]))
    model_s3_client.add_cardinality_constraint(np.array([1, 0, 1, 0]), 2)
    model_s3_client.add_equality_constraint(np.array([44.01, 0, 10, -1], dtype=np.float32), -50.01)
    model_s3_client.add_inequality_constraint(np.array([44.01, 0, 10, -1], dtype=np.float32), np.array([np.nan, 10], dtype=np.float32))

    # Send the request
    model_s3_client.optimize()

    # Make sure the appropriate manifest flag have been sent
    assert mock_titanq_client.request_sent.input.manifest.has_set_partitioning_constraint == True
    assert mock_titanq_client.request_sent.input.manifest.has_cardinality_constraint == True
    assert mock_titanq_client.request_sent.input.manifest.has_equality_constraint == True
    assert mock_titanq_client.request_sent.input.manifest.has_inequality_constraint == True