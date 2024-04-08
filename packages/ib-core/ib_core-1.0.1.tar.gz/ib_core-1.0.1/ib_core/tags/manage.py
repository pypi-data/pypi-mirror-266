import requests

from ib_core.mixins.authorization import AuthorizationReader
from ib_core.utils.urls_manager import generate_url
from ib_core import LOCALHOST, HTTP_PROTOCOL, HTTPS_PROTOCOL, USE_DOCKER_NETWORK, DEFAULT_DOCKER_PORT


def create_tag_and_get_text_tag_id(content: str, auth: AuthorizationReader):
    response = requests.post(url=generate_url(
        False, LOCALHOST, 8001, False,
        'tags', 'tag', 'content', 'create',
        container_name="tags-module"
    ),
        headers={"Authorization": f"{auth.auth_type} {auth.token}"},
        json={'content': content})
    try:
        return response.json()['id']
    except Exception:
        return None


def get_tag(uuid: str, auth: AuthorizationReader):
    response = requests.get(url=generate_url(
        False, LOCALHOST, 8001, False,
        'tags', 'tag', 'get', uuid,
        container_name="tags-module"
    ),
        headers={"Authorization": f"{auth.auth_type} {auth.token}"})
    try:
        return response.json()
    except Exception:
        return None


def get_tags_by_value(value: str, auth: AuthorizationReader):
    response = requests.get(url=generate_url(
        False, LOCALHOST, 8001, False,
        'tags', 'list',
        container_name="tags-module", content=value),
        headers={"Authorization": f"{auth.auth_type} {auth.token}"})
    try:
        return response.json()
    except Exception:
        return []


def create_tag_and_get_file_tag_id(file, auth: AuthorizationReader):
    _file = open(file=file, mode='rb')
    response = requests.post(url=generate_url(
        False, LOCALHOST, 8001, False,
        'tags', 'tag', 'file', 'create',
        container_name="tags-module"),
        headers={"Authorization": f"{auth.auth_type} {auth.token}"},
        files={'file': _file})
    try:
        return response.json()['id']
    except Exception:
        return None
