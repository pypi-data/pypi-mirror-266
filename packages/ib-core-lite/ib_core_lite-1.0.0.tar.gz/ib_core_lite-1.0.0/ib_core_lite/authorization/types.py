import typing

EMPTY = ""
BASE_TOKEN_AUTH = "Token"
JWT_AUTH = "Bearer"

auth_types = typing.Literal[
    "Token",
    "Bearer"
]

NONE = ""
BASE_TOKEN = "BaseToken"
JWT = "JWT"

token_types = typing.Literal[
    "BaseToken",
    "JWT"
]
