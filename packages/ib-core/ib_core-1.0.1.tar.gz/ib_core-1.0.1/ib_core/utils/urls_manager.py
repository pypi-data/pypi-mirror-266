from ib_core import LOCALHOST, HTTP_PROTOCOL, HTTPS_PROTOCOL, USE_DOCKER_NETWORK, DEFAULT_DOCKER_PORT

def check_status_code(status_code: int) -> bool:
    """
    Проеверка статус-кода запроса на успех
    :param status_code: int
    :return: True если запрос прошел успешно, иначе False
    """
    if 2 <= status_code / 100 < 3:
        return True
    return False

def create_root_url(use_ssl=False, domain=LOCALHOST, port=None):
    return f"{HTTPS_PROTOCOL if use_ssl else HTTP_PROTOCOL}://{domain}{f':{port}' if port is not None else ''}"


def generate_url(
        use_ssl=False,
        domain=LOCALHOST,
        port: int = None,
        use_ending_slash=False,
        *args: str, container_name: str = '', **kwargs: str):
    url = create_root_url(use_ssl, domain, port) \
        if not USE_DOCKER_NETWORK or not container_name \
        else create_root_url(use_ssl, container_name, DEFAULT_DOCKER_PORT)
    for arg in args:
        url += f"/{arg}"
    if use_ending_slash:
        url += "/"
    if kwargs.keys():
        url += "?"
        for key in kwargs.keys():
            url += f"{key}={kwargs[key]}"
            url += "&"
        url = url[:-1]
    return url
