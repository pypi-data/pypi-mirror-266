from urllib.parse import urlparse
from requests.auth import AuthBase


class BearerAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = f'Bearer {self.token}'
        return r


class EmptyAuth(AuthBase):
    def __call__(self, r):
        return r


def join_url(base_uri: str, *parts):
    if base_uri.endswith('/'):
        base_uri = base_uri[:-1]

    cleaned_parts = [part.strip("/") for part in parts if part is not None and part.strip("/")]
    return f"{base_uri}/{'/'.join(cleaned_parts)}"


def assembly_artifact_url(uri):
    # TODO :: check if this is the only way to ser artifactory url
    parsed_url = urlparse(uri)
    if parsed_url.scheme not in ["http", "https"]:
        raise Exception(f"Not a valid Artifactory URI: {uri}. "
                        f"Artifactory URI example: `https://frogger.jfrog.io/artifactory/ml-local`")

    return f"{parsed_url.scheme}://{parsed_url.netloc}/artifactory"
