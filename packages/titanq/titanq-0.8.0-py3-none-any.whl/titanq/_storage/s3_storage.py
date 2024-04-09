import datetime
from itertools import chain
from typing import Optional
import boto3
import botocore
import logging
import time

from .._client.model import AwsStorage, S3Input, S3Output
from .storage_client import StorageClient

log = logging.getLogger("TitanQ")

_BIAS_FILE = "bias.npy"
_WEIGHTS_FILE = "weights.npy"
_CONSTRAINT_BOUNDS_FILE = "constraint_bounds.npy"
_CONSTRAINT_WEIGHTS_FILE = "constraints_weights.npy"
_VARIABLE_BOUNDS_FILE = "variable_bounds.npy"
_RESULT_FILE = "result.zip"



class S3Storage(StorageClient):
    def __init__(self, access_key, secret_key, bucket_name):
        """
        Initiate the s3 client for handling the temporary files.
        If any aws argument is missing this will raise an exception.

        :param aws_access_key_id: aws access key id used to upload and download files from an aws bucket.
        :param aws_secret_access_key: aws secret access key used to upload and download files from an aws bucket.
        :param aws_bucket_name: name of the aws bucket use to store temporairly data use by the titanq optimizer backend.
        """
        self._s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        self._access_key_id = access_key
        self._secret_access_key = secret_key
        self._bucket_name = bucket_name

        timestamp = datetime.datetime.now().isoformat()
        self._remote_folder = f"titanq_sdk/{timestamp}"

        # keep track of which file were uploaded
        self._file_uploaded = set()

    def _upload_arrays(
        self,
        bias: bytes,
        weights: bytes,
        constraint_bounds: Optional[bytes],
        constraint_weights: Optional[bytes],
        variable_bounds: Optional[bytes]
        ) -> None:

        upload_tuple = [
            (self._get_full_filename(_BIAS_FILE), bias),
            (self._get_full_filename(_WEIGHTS_FILE), weights)
        ]

        if constraint_bounds:
            upload_tuple.append((self._get_full_filename(_CONSTRAINT_BOUNDS_FILE), constraint_bounds))

        if constraint_weights:
            upload_tuple.append((self._get_full_filename(_CONSTRAINT_WEIGHTS_FILE), constraint_weights))

        if variable_bounds:
            upload_tuple.append((self._get_full_filename(_VARIABLE_BOUNDS_FILE), variable_bounds))

        for filename, body in upload_tuple:
            log.debug(f"Uploading object on AWS s3: {filename}")
            self._s3.put_object(Body=body, Bucket=self._bucket_name, Key=filename)
            self._file_uploaded.add(filename)

    def _input(self) -> S3Input:
        constraint_bounds = self._get_full_filename(_CONSTRAINT_BOUNDS_FILE)
        constraint_weights = self._get_full_filename(_CONSTRAINT_WEIGHTS_FILE)
        variable_bounds = self._get_full_filename(_VARIABLE_BOUNDS_FILE)

        return S3Input(
            s3=self._get_api_model_location(),
            weights_file_name=self._get_full_filename(_WEIGHTS_FILE),
            bias_file_name=self._get_full_filename(_BIAS_FILE),
            constraint_weights_file_name=constraint_weights if constraint_weights in self._file_uploaded else None,
            constraint_bounds_file_name=constraint_bounds if constraint_bounds in self._file_uploaded else None,
            variable_bounds_file_name=variable_bounds if variable_bounds in self._file_uploaded else None,
            manifest=None
        )

    def _output(self) -> S3Output:
        return S3Output(
            result_archive_file_name=self._get_full_filename(_RESULT_FILE),
            s3=self._get_api_model_location())

    def _get_api_model_location(self) -> AwsStorage:
        """
        :return: An AwsStorage object that can be used in the api_model using this S3 credentials
        """
        return AwsStorage(
            bucket_name=self._bucket_name,
            access_key_id=self._access_key_id,
            secret_access_key=self._secret_access_key,
        )

    def _wait_for_result_to_be_uploaded_and_download(self) -> bytes:
        result_file = self._get_full_filename(_RESULT_FILE)
        self._wait_for_file_to_be_uploaded(result_file)
        return self._download_file(result_file)

    def _wait_for_file_to_be_uploaded(self, filename: str):
        """
        Wait until a file exist in a bucket. It also verifies if the
        file is bigger than 0 bytes, this will ensure not downloading
        the empty archive file uploaded to test credentials

        :param filename: The full path of the file that is uploaded
        """
        log.debug(f"Waiting until object get upload on AWS s3: {filename}")
        while True:
            try:
                # check if file exist in the s3 bucket
                response = self._s3.head_object(
                    Bucket=self._bucket_name,
                    Key=filename,
                )
                # check if file content_length > 0
                if response['ContentLength'] > 0:
                    break
            except botocore.exceptions.ClientError as ex:
                # if the error we got is not 404, This is an unexpected error. Raise it
                if int(ex.response['Error']['Code']) != 404:
                    raise

            time.sleep(0.25) # wait 0.25 sec before trying again

    def _download_file(self, filename) -> bytes:
        """
        Download file from remote s3 bucket

        :param filename: The full path of the file to be uploaded

        :return: content of the file
        """
        log.debug(f"Downloading object from AWS s3: {filename}")
        object = self._s3.get_object(Bucket=self._bucket_name, Key=filename)
        return object['Body'].read()

    def _delete_remote_object(self):
        """
        Delete remote object on AWS s3

        :param key: object name to be deleted on the remote s3 bucket
        """
        for file_name in chain(self._file_uploaded, [self._get_full_filename(_RESULT_FILE)]):
            log.debug(f"Deleting object on AWS s3: {file_name}")
            self._s3.delete_object(Bucket=self._bucket_name, Key=file_name)

    def _get_full_filename(self, filename: str) -> str:
        return f"{self._remote_folder}/{filename}"