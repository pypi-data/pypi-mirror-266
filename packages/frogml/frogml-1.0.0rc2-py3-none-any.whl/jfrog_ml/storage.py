from abc import ABC, abstractmethod
from typing import Optional


class Storage(ABC):
    """
    Repository storage to download or store model artifacts, metrics and relation between these in an Artifactory
    repository.
    """

    @abstractmethod
    def upload_model_version(
            self,
            repository: str,
            model_name: str,
            source_path: str,
            namespace: Optional[str] = None,
            version: Optional[str] = None,
            tags: Optional[dict[str, str]] = None):
        """ Uploads a model to a repository in Artifactory. Uploaded models should be stored with the following layout:
        ├── REPO
            ├── models
                ├── ${NAMESPACE}
                    ├── ${MODEL_NAME}
                        ├── ${MODEL_VERSION}
                            model
                                ├── model-info.json
                                ├── model.pkl
                                ├── ...
        :param repository: the repository to upload the model to
        :param model_name: the name of the model
        :param source_path: the source path of the model
        :param namespace: the namespace to upload the model to
        :param version: the version of the model
        :param tags: tags to associate with the model
        """
        pass

    @abstractmethod
    def download_model_version(
            self,
            repository: str,
            model_name: str,
            version: str,
            target_path: str,
            namespace: Optional[str] = None):
        """ Downloads a model from an Artifactory repository
        :param repository: the repository to download the model from
        :param model_name: the name of the model to download
        :param version: the version of the model to download
        :param target_path: the target local path to store the model in
        :param namespace: the namespace of the model to download

        """
        pass

    @abstractmethod
    def upload_auxiliary_artifacts(
            self,
            repository: str,
            model_name: str,
            version: str,
            source_path: str,
            namespace: Optional[str] = None):
        """ Upload artifacts that are associated with a specific model version but are not located directly within the
         model directory.
        :param repository: the repository to upload the model from
        :param model_name: the name of the model to upload
        :param version: the version of the model to upload
        :param source_path: the source path of the artifacts
        :param namespace: the namespace of the model to upload
        """
        pass

    def download_artifact(
            self,
            repository: str,
            source_path: str,
            target_path: str):
        """ Downloads an artifact from an Artifactory repository
        :param repository: the repository to download the artifact from
        :param source_path: the source path of the artifact
        :param target_path: the target local path to store the artifact in
        """
        pass
