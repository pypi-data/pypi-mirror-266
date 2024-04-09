import logging
from typing import Optional
import requests
import time
import urllib3

from .._client.model import UrlInput, UrlOutput
from .storage_client import StorageClient
from .._client.client import Client
from .._model.errors import ConnectionError

log = logging.getLogger("TitanQ")


class ManagedStorage(StorageClient):
    def __init__(self, titanq_client: Client):
        """
        Initiate the managed storage client for handling the temporary files.

        :titanq_client: titanq_client to be used to fetch temporary URL's
        """
        self._titanq_client = titanq_client
        self._urls = titanq_client.temp_storage()
        self._constraint_bounds_uploaded = False
        self._constraint_weights_uploaded = False
        self._variable_bounds_uploaded = False

    def _upload_arrays(
        self,
        bias: bytes,
        weights: bytes,
        constraint_bounds: Optional[bytes],
        constraint_weights: Optional[bytes],
        variable_bounds: Optional[bytes]
        ):
        upload_tuple = [
            (self._urls.input.bias_file.upload, bias),
            (self._urls.input.weights_file.upload, weights),
        ]

        if constraint_bounds:
            self._constraint_bounds_uploaded = True
            upload_tuple.append((self._urls.input.constraint_bounds_file.upload, constraint_bounds))

        if constraint_weights:
            self._constraint_weights_uploaded = True
            upload_tuple.append((self._urls.input.constraint_weights_file.upload, constraint_weights))

        if variable_bounds:
            self._variable_bounds_uploaded = True
            upload_tuple.append((self._urls.input.variable_bounds_file.upload, variable_bounds))

        log.debug(f"Uploading files on our temporary storage")
        for url, data in upload_tuple:
            requests.put(url, data=data)


    def _input(self) -> UrlInput:
        return UrlInput(
            weights_file_name=self._urls.input.weights_file.download,
            bias_file_name=self._urls.input.bias_file.download,
            constraint_bounds_file_name=self._urls.input.constraint_bounds_file.download if self._constraint_bounds_uploaded else None,
            constraint_weights_file_name=self._urls.input.constraint_weights_file.download if self._constraint_weights_uploaded else None,
            variable_bounds_file_name=self._urls.input.variable_bounds_file.download if self._variable_bounds_uploaded else None,
            manifest=None
        )

    def _output(self) -> UrlOutput:
        return UrlOutput(result_archive_file_name=self._urls.output.result_archive_file.upload)

    def _wait_for_result_to_be_uploaded_and_download(self) -> bytes:
        self._wait_for_file_to_be_uploaded(self._urls.output.result_archive_file.download)
        return self._download_file(self._urls.output.result_archive_file.download)

    def _wait_for_file_to_be_uploaded(self, url: str):
        """
        Wait until the content of the file in the temporary storage is bigger
        than 0 bytes. Meaning it will wait until the file is uploaded

        :param url: Url to download the file.
        """
        retries = 0

        while retries < 5:
            try:
                response = requests.get(url)
                response.raise_for_status()
                if len(response.content) > 0:
                    return

            except (urllib3.exceptions.ProtocolError, requests.exceptions.ConnectionError, ConnectionResetError) as e:
                retries = retries + 1
                log.warning(f"Caught error {e} [retries: {retries}]")
                time.sleep(1.0)

            time.sleep(0.25)

        raise ConnectionError("Unexpected error with InfinityQ internal storage, please contact InfinityQ support for more information")

    def _download_file(self, url) -> bytes:
        """
        Download file from the temporary storage

        :param url: Url to download the file.

        :return: content of the file in bytes
        """
        log.debug(f"Downloading object from the temporary storage")
        request = requests.get(url)
        return request.content

    def _delete_remote_object(self) -> None:
        log.debug("Temporary storage option does not delete any file at the moment")