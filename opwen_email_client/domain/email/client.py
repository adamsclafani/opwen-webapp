from abc import ABCMeta
from abc import abstractmethod
from typing import Tuple

from requests import Response
from requests import get as http_get
from requests import post as http_post


class EmailServerClient(metaclass=ABCMeta):
    @abstractmethod
    def upload(self, resource_id: str, container: str):
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def download(self) -> Tuple[str, str]:
        raise NotImplementedError  # pragma: no cover


class HttpEmailServerClient(EmailServerClient):
    _supported_resource_type = 'azure-blob'

    def __init__(self, read_api: str, write_api: str, client_id: str):
        self._read_api = read_api
        self._write_api = write_api
        self._client_id = client_id

    @property
    def _upload_url(self) -> str:
        return 'http://{host}/api/email/lokole'.format(
            host=self._write_api)

    @property
    def _download_url(self) -> str:
        return 'http://{host}/api/email/lokole'.format(
            host=self._read_api)

    @property
    def _auth_headers(self) -> dict:
        return {
            'X-LOKOLE-ClientId': self._client_id,
        }

    def upload(self, resource_id, container):
        payload = {
            'resource_id': resource_id,
            'container_name': container,
            'resource_type': self._supported_resource_type,
        }

        response = http_post(self._upload_url, json=payload,
                             headers=self._auth_headers)
        response.raise_for_status()

    def download(self):
        response = http_get(self._download_url, headers=self._auth_headers)
        response.raise_for_status()

        resource_id, resource_container = self._validate(response)

        return resource_id, resource_container

    def _validate(self, response: Response):
        try:
            payload = response.json()
        except ValueError:
            payload = {}

        resource_id = payload.get('resource_id', '')
        resource_container = payload.get('resource_container', '')
        resource_type = payload.get('resource_type', '').lower()

        if resource_type and resource_type != self._supported_resource_type:
            raise ValueError('unsupported resource type: {}'
                             .format(resource_type))

        return resource_id, resource_container
