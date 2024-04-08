import typing

import requests

from ib_core_lite.settings import LOCALHOST
from ib_core_lite.utils import generate_url

auth_types = typing.Literal[
    "Token",
    "Bearer"
]


def token_authorization(_token, auth_type: auth_types):
    url = generate_url(True, "ib-elp.psg.su", None, False, "ib_auth", "authorization",
                       "token" if auth_type == "Token" else "jwt")
    auth = requests.get(
        url=url,
        headers={
            "Authorization": f"{auth_type} {_token}"
        }
    )
    if int(auth.status_code / 100) >= 5:
        return {"message": "Authorization server returned fatal error"}, auth.status_code
    return auth.json(), auth.status_code


def get_auth_header(request):
    return request.headers.get("Authorization", "")


def get_auth_info(authorization: str):
    if not authorization:
        auth_type, token = "", ""
    else:
        try:
            auth_type, token = tuple(authorization.split(' ', 1))
        except Exception as ex:  # noqa
            auth_type, token = "", ""
    return auth_type, token


def check_group_permission(auth_content: str, group_data):
    response = requests.post(
        url=generate_url(False, LOCALHOST, 8001, False, "user", "group", "operations", "check", "list"),
        json={"groups": group_data},
        headers={
            "Authorization": auth_content
        }
    )
    print(response.json())
    try:
        return response.json()["has_permission"]
    except:  # noqa
        return False
