import datetime
import pytest
import requests
import requests_mock

from pydantic import ValidationError

from titanq._client import Client, api_model
from titanq import errors

@pytest.fixture
def solve_request():
    return api_model.SolveRequest(
        input=api_model.S3Input(
            s3=api_model.AwsStorage(
                bucket_name="test_input_bucket",
                access_key_id="test_access_key",
                secret_access_key="test_secret_access_key",
            ),
            bias_file_name='test_bias_file_name.npy',
            weights_file_name='test_weights_file_name.npy',
            constraint_bounds_file_name=None,
            constraint_weights_file_name=None,
            variable_bounds_file_name=None,
            manifest=api_model.Manifest(
                has_set_partitioning_constraint= False,
                has_cardinality_constraint= False,
                has_equality_constraint=False,
                has_inequality_constraint=False
            ),
        ),
        output=api_model.S3Output(
                result_archive_file_name="test.zip",
                s3=api_model.AwsStorage(
                bucket_name="test_output_bucket",
                access_key_id="test_access_key",
                secret_access_key="test_secret_access_key",
            )
        ),
        parameters=api_model.Parameters(
            beta=[0.1],
            coupling_mult=0.5,
            num_chains=8,
            num_engines=2,
            timeout_in_secs=10,
            variable_types='binary',
            normalized=True,
        )
    )

@pytest.fixture
def baseurl():
    return "https://unittest.titanq.infinityq.io"

@pytest.fixture
def client(baseurl):
    return Client("test_api_key", baseurl)

@pytest.fixture
def temp_storage_raw_response():
    return \
        '{"input": {' \
            '"weights.npy": { "upload": "http://weights-upload.com", "download": "http://weights-download.com" },' \
            '"bias.npy": { "upload": "http://bias-upload.com", "download": "http://bias-download.com" }, ' \
            '"constraint_weights.npy": { "upload": "http://constraint_weights-upload.com", "download": "http://constraint_weights-download.com" }, ' \
            '"constraint_bounds.npy": { "upload": "http://constraint_bounds-upload.com", "download": "http://constraint_bounds-download.com" }, ' \
            '"variable_bounds.npy": { "upload": "http://variable_bounds-upload.com", "download": "http://variable_bounds-download.com" } }, ' \
        '"output": {' \
            '"result.zip": { "upload": "http://result-upload.com", "download": "http://result-download.com" } } }'

def test_temp_storage(client, baseurl, temp_storage_raw_response):
    with requests_mock.Mocker() as m:
        adapter = m.get(f'{baseurl}/v1/temp_storage', content=temp_storage_raw_response.encode())
        temp_storage_response = client.temp_storage()

    assert adapter.call_count == 1
    assert adapter.last_request.headers['authorization'] == 'test_api_key'

    assert temp_storage_response.input.weights_file.upload == "http://weights-upload.com"
    assert temp_storage_response.input.weights_file.download == "http://weights-download.com"
    assert temp_storage_response.input.bias_file.upload == "http://bias-upload.com"
    assert temp_storage_response.input.bias_file.download == "http://bias-download.com"
    assert temp_storage_response.input.constraint_weights_file.upload == "http://constraint_weights-upload.com"
    assert temp_storage_response.input.constraint_weights_file.download == "http://constraint_weights-download.com"
    assert temp_storage_response.input.constraint_bounds_file.upload == "http://constraint_bounds-upload.com"
    assert temp_storage_response.input.constraint_bounds_file.download == "http://constraint_bounds-download.com"
    assert temp_storage_response.input.variable_bounds_file.upload == "http://variable_bounds-upload.com"
    assert temp_storage_response.input.variable_bounds_file.download == "http://variable_bounds-download.com"
    assert temp_storage_response.output.result_archive_file.upload == "http://result-upload.com"
    assert temp_storage_response.output.result_archive_file.download == "http://result-download.com"

def test_credits(client, baseurl):
    raw_credit_response = '{"remaining_credits": 10,"expiration_date": "2023-12-13T16:44:00+00:00"}'

    with requests_mock.Mocker() as m:
        adapter = m.get(f'{baseurl}/v1/credits', content=raw_credit_response.encode())
        credit_response = client.credits()

    assert adapter.call_count == 1
    assert adapter.last_request.headers['authorization'] == 'test_api_key'

    assert credit_response.expiration_date == datetime.datetime(2023, 12, 13, 16, 44, tzinfo=datetime.timezone.utc)
    assert credit_response.remaining_credits == 10


def test_credits_unexpected_error(client, baseurl):
    with requests_mock.Mocker() as m:
        m.get(f'{baseurl}/v1/credits', status_code=500)
        with pytest.raises(requests.exceptions.HTTPError):
            client.credits()

def test_solve_queued(client, baseurl, solve_request):
    raw_solve_response = '{ "computation_id": "test_id", "status": "Queued", "message": "test_message"}'
    with requests_mock.Mocker() as m:
        adapter = m.post(f'{baseurl}/v1/solve', content=raw_solve_response.encode())
        solve_response = client.solve(solve_request)

        assert adapter.call_count == 1
        assert adapter.last_request.headers['authorization'] == 'test_api_key'
        assert adapter.last_request.text == solve_request.model_dump_json()

        assert solve_response.computation_id == "test_id"
        assert solve_response.status == "Queued"
        assert solve_response.message == "test_message"


def test_solve_rejected(client, baseurl, solve_request):
    raw_solve_response = '{ "computation_id": "test_id", "status": "Rejected", "message": "test_message"}'
    with requests_mock.Mocker() as m:
        m.post(f'{baseurl}/v1/solve', content=raw_solve_response.encode())
        with pytest.raises(errors.ServerError):
            client.solve(solve_request)


def test_solve_validation_error(client, baseurl, solve_request):
    raw_solve_response = '{ "non_existant_field": "test_id", "status": "Queued", "message": "test_message"}'
    with requests_mock.Mocker() as m:
        m.post(f'{baseurl}/v1/solve', content=raw_solve_response.encode())
        with pytest.raises(ValidationError):
            client.solve(solve_request)


def test_solve_unexpected_error(client, baseurl, solve_request):
    with requests_mock.Mocker() as m:
        m.post(f'{baseurl}/v1/solve', status_code=500)
        with pytest.raises(requests.exceptions.HTTPError):
            client.solve(solve_request)
