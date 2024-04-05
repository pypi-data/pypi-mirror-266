from typing import Optional

from jfrog_ml.constants import FROG_ML_CONFIG_ARTIFACTORY_URL, SERVER_ID, FROG_ML_CONFIG_ACCESS_TOKEN, \
    FROG_ML_CONFIG_PASSWORD, FROG_ML_CONFIG_USER


class AuthConfig(object):
    def __init__(self, artifactory_url=None, access_token=None, user=None, password=None,
                 server_id: Optional[str] = None):
        self.artifactory_url = artifactory_url
        self.user = user
        self.password = password
        self.access_token = access_token
        self.server_id = server_id

    def to_json(self):
        include_keys = [FROG_ML_CONFIG_ARTIFACTORY_URL, FROG_ML_CONFIG_USER, FROG_ML_CONFIG_PASSWORD,
                        FROG_ML_CONFIG_ACCESS_TOKEN, SERVER_ID]
        return {key: getattr(self, key) for key in include_keys if getattr(self, key) is not None}

    @classmethod
    def by_access_token(cls, artifactory_url: str, access_token: str):
        return cls(
            artifactory_url=artifactory_url,
            access_token=access_token,
        )

    @classmethod
    def by_basic_auth(cls, artifactory_url: str, user: str, password: str):
        return cls(
            artifactory_url=artifactory_url,
            user=user,
            password=password,
        )

    @classmethod
    def by_server_id(cls, server_id: str):
        return cls(
            server_id=server_id
        )

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            artifactory_url=data.get(FROG_ML_CONFIG_ARTIFACTORY_URL),
            access_token=data.get(FROG_ML_CONFIG_ACCESS_TOKEN),
            server_id=data.get(SERVER_ID),
            user=data.get(FROG_ML_CONFIG_USER),
            password=data.get(FROG_ML_CONFIG_PASSWORD),
        )
