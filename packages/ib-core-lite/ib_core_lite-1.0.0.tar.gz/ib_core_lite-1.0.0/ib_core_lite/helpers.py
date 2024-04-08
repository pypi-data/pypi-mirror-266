from typing import TypeVar
import requests

from ib_core_lite.types import NoneData
from ib_core_lite.utils import check_status_code, generate_url
from ib_core_lite.settings import LOCALHOST

T = TypeVar('T')
TPort = TypeVar('TPort', int, None)
THeaders = TypeVar('THeaders', dict, None)
TData = TypeVar('TData', dict, None)


class METHODS:
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class ResponseData:
    def __init__(self, **attributes):
        for key, value in attributes.items():
            if isinstance(value, dict):
                setattr(self, key, ResponseData(**value))
            elif isinstance(value, list):
                setattr(self, key, [ResponseData(**item) if isinstance(item, dict) else item for item in value])
            else:
                setattr(self, key, value)

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return NoneData

    def to_dict(self) -> dict:
        obj_dict = {}
        for key, value in self.__dict__.items():
            if isinstance(value, ResponseData):
                obj_dict[key] = value.to_dict()
            elif isinstance(value, list):
                obj_dict[key] = [item.to_dict() if isinstance(item, Response) else item for item in value]
            else:
                obj_dict[key] = value
        return obj_dict

    def __str__(self):
        return str(self.to_dict())


class Response:
    status: int
    data: ResponseData
    success: bool

    def __init__(self, status: int, **data):
        self.status = status
        self.data = ResponseData(**data)
        self.success = check_status_code(status)


class Request:
    METHODS = METHODS

    @classmethod
    def _resp_has_json(cls, status) -> bool:
        return 2 <= status / 100 < 3 or 4 <= status / 100 < 5

    @classmethod
    def request(
            cls,
            *url_args: str,
            method: str,
            local: bool = True,
            port: TPort = None,
            use_ending_slash: bool = False,
            domain: str = "",
            container_name: str = "",
            headers: THeaders = None,
            data: TData = None,
            **url_kwargs
    ):
        url = generate_url(
            not local, LOCALHOST if local else domain, port, use_ending_slash,
            *url_args, container_name=container_name, **url_kwargs
        )
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data
        )
        data, status = response.json() if cls._resp_has_json(response.status_code) else dict(), response.status_code
        return Response(status, **data)

    @classmethod
    def get(
            cls,
            *url_args: str,
            local: bool = True,
            port: TPort = None,
            use_ending_slash: bool = False,
            domain: str = "",
            container_name: str = "",
            headers: THeaders = None,
            data: TData = None,
            **url_kwargs
    ):
        return cls.request(
            *url_args,
            method=METHODS.GET,
            local=local,
            port=port,
            use_ending_slash=use_ending_slash,
            domain=domain,
            container_name=container_name,
            headers=headers,
            data=data,
            **url_kwargs
        )

    @classmethod
    def post(
            cls,
            *url_args: str,
            local: bool = True,
            port: TPort = None,
            use_ending_slash: bool = False,
            domain: str = "",
            container_name: str = "",
            headers: THeaders = None,
            data: TData = None,
            **url_kwargs
    ):
        return cls.request(
            *url_args,
            method=METHODS.POST,
            local=local,
            port=port,
            use_ending_slash=use_ending_slash,
            domain=domain,
            container_name=container_name,
            headers=headers,
            data=data,
            **url_kwargs
        )

    @classmethod
    def put(
            cls,
            *url_args: str,
            local: bool = True,
            port: TPort = None,
            use_ending_slash: bool = False,
            domain: str = "",
            container_name: str = "",
            headers: THeaders = None,
            data: TData = None,
            **url_kwargs
    ):
        return cls.request(
            *url_args,
            method=METHODS.PUT,
            local=local,
            port=port,
            use_ending_slash=use_ending_slash,
            domain=domain,
            container_name=container_name,
            headers=headers,
            data=data,
            **url_kwargs
        )

    @classmethod
    def patch(
            cls,
            *url_args: str,
            local: bool = True,
            port: TPort = None,
            use_ending_slash: bool = False,
            domain: str = "",
            container_name: str = "",
            headers: THeaders = None,
            data: TData = None,
            **url_kwargs
    ):
        return cls.request(
            *url_args,
            method=METHODS.PATCH,
            local=local,
            port=port,
            use_ending_slash=use_ending_slash,
            domain=domain,
            container_name=container_name,
            headers=headers,
            data=data,
            **url_kwargs
        )

    @classmethod
    def delete(
            cls,
            *url_args: str,
            local: bool = True,
            port: TPort = None,
            use_ending_slash: bool = False,
            domain: str = "",
            container_name: str = "",
            headers: THeaders = None,
            data: TData = None,
            **url_kwargs
    ):
        return cls.request(
            *url_args,
            method=METHODS.DELETE,
            local=local,
            port=port,
            use_ending_slash=use_ending_slash,
            domain=domain,
            container_name=container_name,
            headers=headers,
            data=data,
            **url_kwargs
        )
