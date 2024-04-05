from jfrog_ml._storage_utils import calc_sha2, calc_content_sha2
import os

from pydantic import BaseModel
from typing import List


class Checksums(BaseModel):
    sha2: str

    @classmethod
    def calc_checksums(cls, file_path: str):
        return cls(sha2=calc_sha2(file_path))

    @classmethod
    def calc_content_checksums(cls, content: str):
        return cls(sha2=calc_content_sha2(content))


class Artifact(BaseModel):
    artifact_path: str
    size: int
    checksums: Checksums


class ModelInfo(BaseModel):
    """
    Represent a model information file

    Attributes:
        created_date: The date the model was uploaded to Artifactory
        artifacts: A list of artifacts that belong to the model
    """
    created_date: str
    artifacts: List[Artifact]

    def add_file(self, file_path: str, checksums: Checksums, rel_path: str = None):
        self.artifacts.append(Artifact(artifact_path=rel_path, size=os.path.getsize(file_path), checksums=checksums))

    def add_content_file(self, rel_path: str, content: str = None):
        checksums = Checksums.calc_content_checksums(content)
        self.artifacts.append(
            Artifact(artifact_path=rel_path, size=len(bytes(content, "utf-8")), checksums=checksums))

    @classmethod
    def from_json(cls, json_str: str):
        return cls.model_validate_json(json_str)

    def to_json(self):
        return self.model_dump_json()
