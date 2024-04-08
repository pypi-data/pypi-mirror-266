from ipaddress import ip_network, ip_address

from fastapi.responses import JSONResponse
from starlette import status
from starlette.requests import Request

from ib_core_lite.authorization.types import *
from ib_core_lite.authorization.utils import get_auth_info, token_authorization, check_group_permission


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
    user_id = None

    def __init__(self, request, user_id: str = None):
        self.user_id = user_id
        self._get_authorization(request)

    def _get_authorization(self, request):
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
    tokens: list[Token] = [Token(BASE_TOKEN), Token(JWT)]
    auth = None
    permission_groups: typing.List[str] = []
    only_admins = False
    message = None
    status = None
    market_id = None
    net1 = ip_network("10.0.0.0/8")
    net2 = ip_network("100.64.0.0/10")
    net3 = ip_network("172.16.0.0/12")
    net4 = ip_network("192.168.0.0/16")
    net5 = ip_network("127.0.0.0/8")
    DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000000"
    USER_ID_HEADER = "X-UserID"

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.dispatch(self.get_property("request"))

    def get_property(self, key):
        return getattr(self, key)

    def generate_exception(self):
        print(self.status, self.message)
        return JSONResponse(status_code=self.status, content={"detail": self.message})

    def permission_groups_to_data(self):
        return [{"name": group} for group in self.permission_groups]

    def check_token(self):
        if not self.tokens or not isinstance(self.tokens, list):
            raise Exception("'tokens' should be 'Token's objects list")

    def get_allowed_authorization_types(self):
        return [_token.auth_type for _token in self.tokens]

    def set_message_and_status(self, message: str, _status: int):
        self.message = message
        self.status = _status

    @classmethod
    def is_local_address(cls, request):
        ADDRESS = request.client.host
        print(ADDRESS)
        return ip_address(ADDRESS) in cls.net1 or ip_address(ADDRESS) in cls.net2 or ip_address(
            ADDRESS) in cls.net3 or ip_address(
            ADDRESS) in cls.net4 or ip_address(
            ADDRESS) in cls.net5

    def get_market(self, request):
        self.market_id = request.headers.get("market")

    def dispatch(self, request: Request, *args, **kwargs):
        self.get_market(request)
        if self.is_local_address(request):
            self.user_id = request.headers.get(self.USER_ID_HEADER)
            if self.user_id:
                self.auth = AuthorizationReader(request, self.user_id)
                self.set_message_and_status(message="Авторизован", _status=200)
                return
        self.check_token()
        allowed_authorization_types = self.get_allowed_authorization_types()
        self.auth = AuthorizationReader(request)
        if not self.auth.authorization:
            self.message = "Учетные данные не были предоставлены."
            self.status = status.HTTP_401_UNAUTHORIZED
            return

        if self.auth.auth_type not in allowed_authorization_types:
            self.message = "Некорректный тип авторизации."
            self.status = status.HTTP_401_UNAUTHORIZED
            return

        response, _status = token_authorization(
            self.auth.token,
            self.auth.auth_type
        )

        if not (2 <= int(_status / 100) < 3):
            self.set_message_and_status(response.get("detail"), _status)
            return

        self.user = AuthUser(**response)
        self.user_id = self.user.get_id()
        self.auth.user_id = self.user_id
        if self.only_admins and not self.user.is_superuser:
            self.message = "Доступ запрещен."
            self.status = status.HTTP_403_FORBIDDEN
            return
        self.set_message_and_status(message="Авторизован", _status=200)
        return
