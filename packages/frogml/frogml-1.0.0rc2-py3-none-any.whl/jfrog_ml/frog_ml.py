import concurrent
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Optional

from jfrog_ml._artifactory_api import ArtifactoryApi
from jfrog_ml._log_config import logger
from jfrog_ml.model_info import ModelInfo, Checksums
from jfrog_ml.storage import Storage
from jfrog_ml._utils import join_url, assembly_artifact_url
from jfrog_ml.authentication._authentication_utils import get_credentials
from jfrog_ml.authentication.models._auth_config import AuthConfig


class FrogML(Storage):
    """
    Repository implementation to download or store model artifacts, and metrics in Artifactory repository.
    """

    def __init__(self, login_config: AuthConfig = None):
        uri, auth = get_credentials(login_config)
        self.uri = assembly_artifact_url(uri)
        self.auth = auth
        self.artifactory_api = ArtifactoryApi(self.uri, self.auth)
        self.__set_up_thread_pool()

    def __set_up_thread_pool(self):
        self.http_threads_count = os.getenv("JFML_HTTP_THREADS_COUNT")
        try:
            self.http_threads_count = int(self.http_threads_count)
        except (TypeError, ValueError):
            logger.debug(f"Error: JFML_HTTP_THREADS_COUNT is not a valid integer. Using default value (5).")
            self.http_threads_count = 5

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.http_threads_count)

    def upload_model_version(
            self,
            repository: str,
            model_name: str,
            source_path: str,
            namespace: Optional[str] = None,
            version: Optional[str] = None,
            properties: Optional[dict[str, str]] = None):
        namespace_and_name = self.__union_model_name_with_namespace(namespace, model_name)
        location_to_upload, transaction_id = self.artifactory_api.start_transaction(repository=repository,
                                                                                    model_name=namespace_and_name,
                                                                                    version=version)
        if not os.path.exists(source_path):
            raise ValueError(f"Provided source_path does not exists : '{source_path}'")
        transaction_date = self.__milliseconds_to_iso_instant(transaction_id)
        model_info = ModelInfo(created_date=transaction_date, artifacts=[])

        if version is None:
            version = location_to_upload.replace(f'models/{namespace_and_name}/tmp/', "").split('/')[0]

        self.__upload_by_source(source_path, repository, location_to_upload, model_name, version, model_info)

        self.artifactory_api.end_transaction(repository=repository, model_name=namespace_and_name,
                                             model_info=model_info, transaction_id=transaction_id, version=version,
                                             properties=properties)
        return model_info

    def download_model_version(
            self,
            repository: str,
            model_name: str,
            version: str,
            target_path: str,
            namespace: Optional[str] = None):
        try:
            download_args = []
            model_info = self.artifactory_api.get_model_info(repository, namespace, model_name, version)
            search_under_repo = f"/{repository}/"

            for artifact in model_info["artifacts"]:
                download_url = artifact["download_url"]
                artifact_path = artifact["artifact_path"]
                position_under_repo = download_url.find(search_under_repo)
                if position_under_repo != -1:
                    repo_rel_path = download_url[position_under_repo + len(search_under_repo):]

                    if not os.path.exists(target_path + "/" + artifact_path):
                        self.__create_dirs_if_needed(target_path, artifact_path)
                        download_args.append((repository, repo_rel_path, target_path + "/" + artifact_path))

            if len(download_args) > 0:
                logger.info(f"\nFetching: {len(download_args)} files.")
                futures = []
                for download_arg in download_args:
                    future = self.executor.submit(self.artifactory_api.download_file, download_arg)
                    futures.append(future)

                successfully_downloaded = self.__submit_and_handle_futures(futures)
                if successfully_downloaded > 0:
                    logger.info(
                        f'\nModel: "{model_name}", version: "{version}" has been downloaded successfully')

            else:
                logger.info(f"\nFiles already exists.")

        except Exception as e:
            logger.error(f"An error occurred during download_model_version: {e}", exc_info=True)

    def upload_auxiliary_artifacts(
            self,
            repository: str,
            model_name: str,
            version: str,
            source_path: str,
            namespace: Optional[str] = None):
        namespace_and_name = self.__union_model_name_with_namespace(namespace, model_name)
        mode_info = self.artifactory_api.get_model_info(repository, namespace, model_name, version)
        if mode_info is not None:
            location_to_upload = f"models/{namespace_and_name}/{version}/artifacts/"
            self.__upload_by_source(source_path, repository, location_to_upload, model_name, version, None)
        else:
            logger.error(
                f'Could not find model info for {namespace_and_name} version {version} in repository {repository}')

    def get_model_info(self, repository: str, namespace: Optional[str], model_name: str, version: Optional[str]):
        return self.artifactory_api.get_model_info(repository, namespace, model_name, version)

    def __upload_by_source(self, source_path: str, repository: str, location_to_upload: str,
                           model_name: str, version: str, model_info: Optional[ModelInfo] = None):
        if os.path.isfile(source_path):
            rel_path = os.path.basename(source_path)
            self.__upload_single_file((repository, source_path, rel_path, location_to_upload, model_info))
        else:
            futures = []
            for dir_path, dir_names, file_names in os.walk(source_path):
                for filename in file_names:
                    full_path = os.path.join(dir_path, filename)
                    rel_path = os.path.relpath(full_path, source_path)
                    future = self.executor.submit(self.__upload_single_file,
                                                  (repository, full_path, rel_path, location_to_upload, model_info))
                    futures.append(future)

            successfully_uploaded = self.__submit_and_handle_futures(futures)

            if successfully_uploaded > 0:
                logger.info(
                    f'\nModel: "{model_name}", version: "{version}" has been uploaded successfully')

    @staticmethod
    def __submit_and_handle_futures(futures):
        failed_futures = []
        for future in futures:
            try:
                future.result()
            except Exception as e:
                failed_futures.append(e.args)

        if len(failed_futures) > 0:
            for failed_future in failed_futures:
                logger.error(f"{failed_future}")

        return len(futures) - len(failed_futures)

    def __upload_single_file(self, args):
        repository, full_path, rel_path, location_to_upload, model_info = args
        if not self.__is_file_ignored(full_path=full_path):
            checksums = Checksums.calc_checksums(full_path)
            if model_info is not None:
                model_info.add_file(full_path, checksums, rel_path)
            url = join_url(self.uri, repository, location_to_upload, rel_path)
            is_checksum_deploy_success = self.artifactory_api.checksum_deployment(url=url, checksum=checksums,
                                                                                  full_path=full_path, stream=True)
            if is_checksum_deploy_success is False:
                self.artifactory_api.upload_file(url=url, file_path=full_path)

    @staticmethod
    def __is_file_ignored(full_path: str) -> bool:
        return os.path.basename(full_path) == ".DS_Store"

    @staticmethod
    def __union_model_name_with_namespace(namespace: str, model_name: str):
        if namespace is None:
            return model_name
        else:
            return namespace + "/" + model_name

    @staticmethod
    def __create_dirs_if_needed(base_dir, file_uri):
        full_path = os.path.join(base_dir, file_uri.strip("/"))
        dest_path = os.path.dirname(full_path)
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        return dest_path

    @staticmethod
    def __milliseconds_to_iso_instant(milliseconds):
        instant = datetime.utcfromtimestamp(int(milliseconds) / 1000.0).replace(tzinfo=timezone.utc)
        x = instant.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4]
        return x
