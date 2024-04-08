import typing

EMPTY = ""
BASE_TOKEN_AUTH = "Token"
JWT_AUTH = "Bearer"

auth_types = typing.Literal[
    "Token",
    "Bearer"
]
