import typing
from ipaddress import ip_network, ip_address

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from rest_framework import status

from ib_core.tokens.models import Token
from ib_core.tokens.types import BASE_TOKEN, JWT
from ib_core import LOCALHOST
from ib_core.utils.authorization import token_authorization, get_auth_info, check_group_permission
from ib_core.utils.uuid_manager import is_valid_uuid


class AuthUser:
    """
    User model for external authorization
    """

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_username(self):
        return getattr(self, 'username')

    def get_id(self):
        return getattr(self, 'id')

    def is_superuser(self):
        return getattr(self, 'is_superuser')


class AuthorizationReader:
    """
    Request authorization header reader class
    """
    authorization = None
    auth_type = None
    token = None
    user_id: None

    def __init__(self, request: WSGIRequest, user_id: str = None):
        self.user_id = user_id
        self._get_authorization(request)

    def _get_authorization(self, request: WSGIRequest):
        self.authorization = request.headers.get("Authorization", "")
        self.auth_type, self.token = get_auth_info(self.authorization)

    def get_authorization_header_content(self):
        return f"{self.auth_type} {self.token}" if not self.user_id else self.user_id


class TokenAuthorizationMixin:
    """
    Uses external authorization of the IB-ELP Auth module.

    Usage:
        1) add mixin to view;
        2) define the types of tokens

    """
    user = None
    user_id = None
    tokens: typing.List[Token] = [Token(BASE_TOKEN), Token(JWT)]
    auth = None
    permission_groups: typing.List[str] = []
    only_admins = False

    DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000000"
    USER_ID_HEADER = "X-UserID"

    net1 = ip_network("10.0.0.0/8")
    net2 = ip_network("100.64.0.0/10")
    net3 = ip_network("172.16.0.0/12")
    net4 = ip_network("192.168.0.0/16")

    def __init__(self):
        pass

    @classmethod
    def is_local_address(cls, request):
        ADDRESS = request.META['REMOTE_ADDR']
        print(ADDRESS)
        return ip_address(ADDRESS) in cls.net1 or ip_address(ADDRESS) in cls.net2 or ip_address(ADDRESS) in cls.net3 or ip_address(
            ADDRESS) in cls.net4

    def permission_groups_to_data(self):
        return [{"name": group} for group in self.permission_groups]

    def check_token(self):
        if not self.tokens or not isinstance(self.tokens, list):
            raise Exception("'tokens' should be 'Token's objects list")

    def get_allowed_authorization_types(self):
        return [_token.auth_type for _token in self.tokens]

    def dispatch(self, request: WSGIRequest, *args, **kwargs):
        if self.is_local_address(request):
            self.user_id = request.headers.get(self.USER_ID_HEADER)
            if self.user_id:
                self.auth = AuthorizationReader(request, self.user_id)
                return super().dispatch(request, *args, **kwargs)  # noqa
        self.check_token()
        allowed_authorization_types = self.get_allowed_authorization_types()
        self.auth = AuthorizationReader(request)
        if not self.auth.authorization:
            return JsonResponse(
                {
                    "detail": "Учетные данные не были предоставлены."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        if self.auth.auth_type not in allowed_authorization_types:
            return JsonResponse(
                {
                    "detail": "Некорректный тип авторизации."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        response, _status = token_authorization(
            self.auth.token,
            self.auth.auth_type
        )

        if not(2 <= int(_status / 100) < 3):
            return JsonResponse(
                response, status=_status
            )

        self.user = AuthUser(**response)
        self.user_id = self.user.get_id()
        if self.only_admins and not self.user.is_superuser:
            return JsonResponse(
                {
                    "detail": "Доступ запрещен."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        if not self.user_id:
            has_permission = check_group_permission(
                self.auth.get_authorization_header_content(),
                self.permission_groups_to_data()
            )
            if not has_permission:
                return JsonResponse(
                    {
                        "detail": "Доступ запрещен."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        return super().dispatch(request, *args, **kwargs)   # noqa


class MarketMixin:

    market_id = None

    def _get_market_header(self, request: WSGIRequest):
        self.market_id = request.headers.get("market")

    def _check_market(self):
        if not is_valid_uuid(self.market_id):
            self.market_id = None

    def dispatch(self, request: WSGIRequest, *args, **kwargs):
        self._get_market_header(request)
        self._check_market()
        if not self.market_id:
            return JsonResponse(
                data=dict(
                    detail="Invalid market ID. Must be a valid uuid4"
                ), status=status.HTTP_403_FORBIDDEN
            )
        return super().dispatch(request, *args, **kwargs)  # noqa
