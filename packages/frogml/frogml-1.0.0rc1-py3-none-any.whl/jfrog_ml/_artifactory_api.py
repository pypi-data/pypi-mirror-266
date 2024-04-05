import json
import os
from typing import Optional

from tqdm.auto import tqdm
from tqdm.utils import CallbackIOWrapper
from urllib3 import Retry

from jfrog_ml.http.http_client import HTTPClient
from jfrog_ml._log_config import logger
from jfrog_ml.model_info import ModelInfo, Checksums
from jfrog_ml._utils import join_url


class ArtifactoryApi:
    def __init__(self, uri, auth=None, http_client=None):
        self.uri = uri
        if http_client is not None:
            self.http_client = http_client
        else:
            self.auth = auth
            self.http_client = HTTPClient(auth=auth)

    def start_transaction(self, repository: str, model_name: str, version: Optional[str]):
        """
            Initializes an upload. Returns transaction ID and upload path
        """
        if version is None:
            start_transaction_url = f"{self.uri}/api/frogml/{repository}/{model_name}/start-transaction"
        else:
            start_transaction_url = f"{self.uri}/api/frogml/{repository}/{model_name}/start-transaction/{version}"

        try:
            response = self.http_client.post(start_transaction_url)
            response.raise_for_status()
            upload_path = response.json()["uploadPath"]
            transaction_id = response.json()["transactionId"]
        except Exception as exception:
            err = f"Error occurred while trying to start an upload transaction for model: '{model_name}' Error: '{exception}'"
            logger.error(err, exc_info=True)
            raise exception
        return upload_path, transaction_id

    def end_transaction(self, repository: str, model_name: str, model_info: ModelInfo, transaction_id: str,
                        version: str, properties: Optional[dict[str, str]]):
        """
            Upload model-info.json file, makes the model available in the repository
        """
        filename = "model-info.json"
        url = join_url(self.uri, "api", "frogml", repository, "model-info", model_name, version, transaction_id,
                       filename)
        json_model_info = model_info.to_json()
        self.upload_model_info(filename, json_model_info, properties, url)

    def get_model_info(self, repository, namespace, model_name, version):
        url = join_url(self.uri, "api", "frogml", repository, "model-info", namespace, model_name, version)
        with self.http_client.get(url=url) as r:
            r.raise_for_status()
            return r.json()

    def download_file(self, args):
        repository, remote_file_path, local_path = args
        filename = os.path.basename(local_path)
        try:
            url = f"{self.uri}/{repository}/{remote_file_path}"
            with self.http_client.get(url=url, stream=True) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))

                with open(local_path, 'wb') as file:
                    with self.__initialize_progress_bar(total_size, filename) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                file.write(chunk)
                                pbar.update(len(chunk))

        except Exception as exception:
            if os.path.exists(local_path):
                os.remove(local_path)
            err = f"Error occurred while trying to download file: '{filename}' Error: '{exception}'"
            logger.error(err, exc_info=True)
            raise type(exception)(f"{err} Filename: {filename}") from exception

    def upload_model_info(self, filename, payload, properties, url, stream=False):
        try:
            files = {
                'modelInfo': ('modelInfo', payload, 'application/octet-stream'),  # Include the InputStream
                'additionalData': ('additionalData', json.dumps(properties), 'application/octet-stream')  # Include the object
            }
            response = self.http_client.put(url=url, files=files, stream=stream)
            response.raise_for_status()
        except Exception as exception:
            err = f"Error occurred while trying to upload file: '{filename}' Error: '{exception}'"
            logger.error(err, exc_info=True)
            raise exception

    def upload_file(self, file_path, url):
        try:
            file_size = os.stat(file_path).st_size
            with (self.__initialize_progress_bar(file_size, file_path) as pbar,
                  open(file_path, "rb") as file):
                wrapped_file = CallbackIOWrapper(pbar.update, file, "read")
                response = self.http_client.put(url=url, payload=wrapped_file)
                response.raise_for_status()
        except Exception as exception:
            err = f"Error occurred while trying to upload file: '{file_path}' Error: '{exception}'"
            logger.error(err, exc_info=True)
            raise type(exception)(f"{err} File: {file_path}") from exception

    def checksum_deployment(self, checksum: Checksums, url, full_path, stream=False):
        response = self.http_client.put(url=url,
                                        headers={"X-Checksum-Sha256": checksum.sha2, "X-Checksum-Deploy": "true"},
                                        stream=stream)
        if response.status_code != 200 and response.status_code != 201:
            return False
        else:
            file_size = os.path.getsize(full_path)
            pbar = self.__initialize_progress_bar(file_size, full_path)
            pbar.update(file_size)
            pbar.close()
            return True

    def get_files_list(self, model_name):
        """
            returns list of files matching the given model name
        """
        url = self.uri + "/api/storage/" + self.repo + "/" + model_name + "?list&deep=1&listFolders=0"
        return self.http_client.get(url=url)

    @staticmethod
    def __initialize_progress_bar(total_size, filename):
        return tqdm(total=total_size, unit='B', unit_scale=True, desc=filename, initial=0)

    def encrypt_password(self):
        """
            returns encrypted password as text
        """
        return self.http_client.get(url=join_url(self.uri, "/api/security/encryptedPassword"))

    def ping(self):
        """
        Sends a ping to Artifactory to validate login status
        """
        url = join_url(self.uri, "api/system/ping")
        return self.http_client.get(url=url)

class RetryWithLog(Retry):
    """
     Adding extra logs before making a retry request
    """

    def __init__(self, *args, **kwargs):
        history = kwargs.get("history")
        if history is not None:
            logger.debug(f'Error: ${history[-1].error}\nretrying...')
        super().__init__(*args, **kwargs)
