import typing

NONE = ""
BASE_TOKEN = "BaseToken"
JWT = "JWT"

token_types = typing.Literal[
    "BaseToken",
    "JWT"
]
