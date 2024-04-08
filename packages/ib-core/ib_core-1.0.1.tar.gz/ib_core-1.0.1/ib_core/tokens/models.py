from ib_core.tokens.auth_types import EMPTY, BASE_TOKEN_AUTH, JWT_AUTH
from ib_core.tokens.types import NONE, BASE_TOKEN, JWT, token_types


class Token:
    """
    Token model for API authorization
    """
    def __init__(self, _type: token_types):
        """
        Token class constructor.

        Keyword arguments:
            _type (token_types): token type. Supports BaseToken and JsonWebToken (from ib_core.tokens.types)
        """
        self._type = _type

    """
    NOT OVERRIDER
    """
    __API_AUTHORIZATION_TYPES = {
        None: EMPTY,
        BASE_TOKEN: BASE_TOKEN_AUTH,
        JWT: JWT_AUTH
    }

    @property
    def type(self):
        return self._type

    @property
    def auth_type(self):
        return self.__API_AUTHORIZATION_TYPES[self._type]

    def __str__(self):
        return str(self._type)
