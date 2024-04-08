from ib_core_lite.settings import HTTPS_PROTOCOL, HTTP_PROTOCOL, LOCALHOST, USE_DOCKER_NETWORK, DEFAULT_DOCKER_PORT


def check_status_code(status_code: int) -> bool:
    """
    Проеверка статус-кода запроса на успех
    :param status_code: int
    :return: True если запрос прошел успешно, иначе False
    """
    if 2 <= status_code / 100 < 3:
        return True
    return False


def create_root_url(use_ssl: bool = False, domain: str = LOCALHOST, port: int | None = None) -> str:
    """
    Генерация корневого URL (протокол + доменное имя)
    :param use_ssl: Использовать ssl (протокол https)
    :param domain: Доменное имя
    :param port: Порт (используется в случае запроса на localhost)
    :return: сгенерированный корневой URL
    """
    return f"{HTTPS_PROTOCOL if use_ssl else HTTP_PROTOCOL}://{domain}{f':{port}' if port is not None else ''}"


def generate_url(
        use_ssl=False,
        domain=LOCALHOST,
        port: int = None,
        use_ending_slash=False,
        *args: str, container_name: str = "", **kwargs: str):
    """
    Генерация URL
    :param use_ssl: Использовать ssl (протокол https).
    :param domain: Доменное имя.
    :param port: Порт (используется в случае запроса на localhost).
    :param use_ending_slash: Поставить слеш ('/') в конце URL
    :param args: параметры для генерации URL. Пример: *args("api", "object", "create") -> "api/object/create"
    :param kwargs: GET параметры запроса. Пример: *kwargs{"query": "example"} -> "?query=example"
    :param container_name
    :return: Сгенерированный URL
    """
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
