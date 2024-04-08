import os


HTTP_PROTOCOL = "http"
HTTPS_PROTOCOL = "https"
LOCALHOST = os.environ.get("LOCALHOST") or '127.0.0.1'

USE_DOCKER_NETWORK = os.environ.get("USE_DOCKER_NETWORK") == 'True' and True
DEFAULT_DOCKER_PORT = 8000



