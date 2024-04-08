#!/usr/bin/env python
# -*- coding:utf-8 -*-
import traceback
from copy import deepcopy
from functools import wraps
from inspect import getfullargspec
from pathlib import Path
from time import sleep

from ._pypkg import Callable
from collections.abc import MutableMapping
from typing import Optional, Union, Any
from urllib.parse import urljoin, urlparse

import regex as re
import ujson as json
from requests import Response, Session
from urllib3 import Retry

from ._hyper.contrib import HTTP20Adapter
from .character import StringBuilder
from .collection.arraylist import ArrayList
from .config.rest import RestConfig
from .decorators import Entity
from .enums import EnhanceEnum
from .exceptions import HttpException, RestInternalException
from .generic import T
from .log import LoggerFactory
from .maps import Dictionary
from .utils.objects import ObjectsUtils
from .utils.strings import StringUtils

_LOGGER = LoggerFactory.get_logger("rest")

_OPTIONAL_ARGS_KEYS = ["params", "data", "json", "headers", "cookies", "files", "auth", "timeout", "allow_redirects",
                       "proxies", "verify", "stream", "cert", "stream", "hooks"]


class _Constant:
    HTTPS = "https"
    SERVER_NAME = "serverName"
    SERVER_HOST = "serverHost"
    OPTS = "opts"
    APIS = "apis"
    API_NAME = "apiName"
    API_PATH = "apiPath"
    DESC = "desc"
    HTTP_METHOD = "httpMethod"
    HEADERS = "headers"
    CONTENT_TYPE = "Content-Type"
    ALLOW_REDIRECTS = "allow_redirects"
    CONTENT_TYPE_DEFAULT = "application/x-www-form-urlencoded"
    CONTENT_TYPE_JSON = "application/json"
    RESPONSE = "response"
    RESTFUL = "restful"


_HTTP_RE = re.compile(f"^http|https?:/{2}\\w.+$")
re.purge()


class RestOptions(Dictionary):
    """
    :param params: (optional) Dictionary or bytes to be sent in the query
            string for the :class:`Request`.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) json to send in the body of the
        :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the
        :class:`Request`.
    :param cookies: (optional) dict or CookieJar object to send with the
        :class:`Request`.
    :param files: (optional) Dictionary of ``'filename': file-like-objects``
        for multipart encoding upload.
    :param auth: (optional) Auth tuple or callable to enable
        Basic/Digest/Custom HTTP Auth.
    :param timeout: (optional) How long to wait for the server to send
        data before giving up, as a float, or a :ref:`(connect timeout,
        read timeout) <timeouts>` tuple.
    :type timeout: float or tuple
    :param allow_redirects: (optional) Set to True by default.
    :type allow_redirects: bool
    :param proxies: (optional) Dictionary mapping protocol or protocol and
        hostname to the URL of the proxy.
    :param stream: (optional) whether to immediately download the response
        content. Defaults to ``False``.
    :param verify: (optional) Either a boolean, in which case it controls whether we verify
        the server's TLS certificate, or a string, in which case it must be a path
        to a CA bundle to use. Defaults to ``True``. When set to
        ``False``, requests will accept any TLS certificate presented by
        the server, and will ignore hostname mismatches and/or expired
        certificates, which will make your application vulnerable to
        man-in-the-middle (MitM) attacks. Setting verify to ``False``
        may be useful during local development or testing.
    :param cert: (optional) if String, path to ssl client cert file (.pem).
        If tuple, ('cert', 'key') pair.
    Usage:
        RestOptions(params={}, data={}, ...)
    """

    def __init__(self, params: dict = None, data: dict = None, headers: dict = None, cookies: dict = None,
                 files: dict = None, auth: tuple = None, timeout: float or tuple = None, allow_redirects: bool = True,
                 proxies: dict = None, hooks: dict = None, stream: bool = None, verify: bool = None, cert: str = None,
                 json: dict = None, restful: dict = None, *args, **kwargs):
        super().__init__()
        self.update(params=params, data=data, headers=headers, cookies=cookies, files=files, auth=auth,
                    timeout=timeout, allow_redirects=allow_redirects, proxies=proxies, hooks=hooks, stream=stream,
                    verify=verify, cert=cert, json=json, restful=restful, **kwargs)

    @property
    def opts_no_none(self) -> Dictionary:
        tmp = Dictionary()
        for k, v in self.items():
            if v:
                tmp[k] = v
        return tmp


class HttpMethod(EnhanceEnum):
    """
    Http method
    """
    GET = "GET"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class RestFul(Dictionary):
    """
    A parameter container specifically for restful
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RestResponse:
    """
    Response wrapper
    """

    def __init__(self, response: Optional[Response]):
        ObjectsUtils.call_limit(__file__)
        if isinstance(response, Response):
            self.__resp: Response = response
        else:
            self.__resp: Response = Response()
            self.__resp._content = b"http request fail"
            self.__resp.status_code = -1

    @property
    def success(self) -> bool:
        """
        check http status code between 200 (inclusive 200) and 300
        :return:
        """
        return self.__resp.status_code <= 200 < 300

    @property
    def code(self) -> int:
        """
        Return http code.
        :return:
        """
        return self.__resp.status_code

    @property
    def content(self) -> bytes:
        return self.__resp.content

    @property
    def text(self):
        return self.__resp.text

    @property
    def headers(self) -> MutableMapping:
        return self.__resp.headers

    @property
    def response(self) -> Response:
        """
        Return origin requests Response
        """
        return self.__resp

    @property
    def body(self) -> Dictionary:
        return Dictionary(self.__resp.json())

    def to_entity(self, type_reference: type[Entity]) -> Union[ArrayList[T], T]:
        """
        :param type_reference: JSON converts the target type of the Python object

        type_reference example:

            @EntityType()
            class Data(Entity):
                id: list[str]
                OK: str
                data: str

        response body:
            {"data":"data content","id":[1],"OK":"200"}



        resp = RestFast("http://localhost:8080").api("/hello").opts(RestOptions(params={"id": 1})).send(Method.GET).response().to_entity(Data)
        print(resp)  # Data(id=[1], OK='200', data='data content')
        """
        if issubclass(type_reference, Entity):
            return type_reference.build_from_dict(self.body)
        raise TypeError(f"excepted type 'Entity' or sub-class, got a {type_reference.__name__}")


class RestFast(object):
    """
    Quickly build a streaming HTTP request client.
    """

    def __init__(self, host, http2: bool = False, retry_times: int = 3, retry_backoff_factor: int = 5):
        self.__host: str = host
        self.__api: str = ""
        self.__opts: RestOptions = RestOptions()
        self.__method: str = HttpMethod.GET.value
        self.__session: Session = Session()
        self.__resp: Optional[Response] = None
        retry = Retry(total=retry_times, backoff_factor=retry_backoff_factor)
        if http2:
            scheme = urlparse(self.__host).scheme
            if scheme != _Constant.HTTPS:
                raise HttpException(f"http2 need https protocol, but found '{scheme}'")
            self.__session.mount(f"{_Constant.HTTPS}://", HTTP20Adapter(max_retries=retry))

    def api(self, api: str) -> 'RestFast':
        """
        set server api
        """
        self.__api = api if api else ""
        return self

    def opts(self, opts: RestOptions) -> 'RestFast':
        """
        http request params, headers, data, json, files etc.
        """
        self.__opts = opts if opts else RestOptions()
        return self

    def send(self, method: HttpMethod) -> 'RestFast':
        """
        set http request method.
        """
        self.__method = method.value if method else HttpMethod.GET.value
        url = f"{self.__host}{self.__api}"
        self.__resp = None
        try:
            self.__resp = getattr(self.__session, self.__method.lower())(url=f"{url}",
                                                                         **self.__opts.opts_no_none)
            return self
        finally:
            if self.__resp:
                content = self.__resp.text if self.__resp else ""
                url_ = self.__resp.url if self.__resp.url else url
                msg = f"http fast request: url={url_}, method={self.__method}, " \
                      f"opts={self.__opts.opts_no_none}, response={StringUtils.abbreviate(content)}"
                _LOGGER.log(level=20, msg=msg, stacklevel=3)
            else:
                msg = f"http fast request no response: url={self.__host}{self.__api}, method={self.__method}, " \
                      f"opts={self.__opts.opts_no_none}"
                _LOGGER.log(level=30, msg=msg, stacklevel=3)

    def response(self) -> RestResponse:
        """
        send request and get response.
        type_reference priority is greater than only_body.
        type_reference will return custom entity object.

        usage:
            type_reference example:

                @EntityType()
                class Data(Entity):
                    id: list[str]
                    OK: str
                    data: str

            response body:
                {"data":"data content","id":[1],"OK":"200"}



            resp = RestFast("http://localhost:8080").api("/hello").opts(RestOptions(params={"id": 1})).send(Method.GET).response().to_entity(Data)
            print(resp)  # Data(id=[1], OK='200', data='data content')
        """
        return RestResponse(self.__resp)

    @staticmethod
    def bulk(content: str) -> dict:
        return Rest.bulk(content)


class Rest(object):
    """
    A simple http request frame.
    """

    def __init__(self, file: str = None, server_name: str = None, host: str = None, herders: dict = None,
                 cookies: dict = None, check_status: bool = False, encoding: str = "utf-8", description: str = None,
                 restful: dict = None, http2: bool = False, retry_times: int = 10, retry_interval: int = 5,
                 retry_exit_code_range: list = None, retry_exception_retry: bool = True,
                 retry_check_handler: Callable[[Any], bool] = None):
        """
            def retry(times: int = 10, interval: int = 5, exit_code_range: list = None, exception_retry: bool = True,
              check_handler: Callable[[Any], bool] = None) -> T:
        Build a request client.
        :param file: The path where the interface configuration file is stored.
                     configuration format：
                        [
                          {
                            "serverName": "s1",
                            "serverHost": "http://localhost1",
                            "desc": "",
                            "apis": [
                              {
                                "apiName": "user",
                                "apiPath": "/user",
                                "httpMethod": "post",
                                "headers": {"Content-type": "multipart/form-data"},
                                "desc": ""
                              }
                            ]
                          },
                          {
                            "serverName": "s2",
                            "serverHost": "http://localhost2",
                            "desc": "",
                            "apis": [
                              {
                                "apiName": "admin",
                                "apiPath": "/admin",
                                "httpMethod": "get",
                                "desc": ""
                              }
                            ]
                          }
                        ]
        :param server_name: Service name, which allows you to read interface information from the interface
        configuration file.
        """
        self.__restful = None
        self.__check_status: Optional[bool] = None
        self.__encoding: Optional[str] = None
        self.__server_name: Optional[str] = None
        self.__server_list: Optional[list[dict[str, str]]] = None
        self.__server: Optional[dict[str, Any]] = None
        self.__host: Optional[str] = None
        self.__headers: Optional[dict[str, str]] = None
        self.__cookies: Optional[dict[str, str]] = None
        self.__description: Optional[str] = None
        self.__http2: Optional[bool] = None
        self.__session: Optional[Session] = None
        self.__retry_times: Optional[int] = None
        self.__retry_interval: Optional[int] = None
        self.__retry_exit_code_range: Optional[list] = None
        self.__retry_exception_retry: Optional[bool] = None
        self.__retry_check_handler: Optional[Callable[[Any], bool]] = None
        self.__initialize(file, server_name, host, herders, cookies, check_status, encoding, description, restful,
                          http2, retry_times, retry_interval, retry_exit_code_range, retry_exception_retry,
                          retry_check_handler)

    def __initialize(self, file: str = None, server_name: str = None, host: str = None, headers: dict[str, str] = None,
                     cookies: dict[str, str] = None, check_status: bool = False, encoding: str = "utf-8",
                     description: str = None, restful: dict = None, http2: bool = False, retry_times: int = 10,
                     retry_interval: int = 5, retry_exit_code_range: list = None, retry_exception_retry: bool = True,
                     retry_check_handler: Callable[[Any], bool] = None):
        self.__restful = restful or RestFul()
        self.__check_status: bool = check_status if isinstance(check_status, bool) else False
        self.__encoding: str = encoding if isinstance(encoding, str) else "utf-8"
        self.__server_name: str = server_name
        self.__server_list: list[dict[str, str]] = []
        self.__server: dict[str, dict[Any, Any]] = {}
        self.__host: str = host
        self.__headers: dict[str, str] = headers or {}
        self.__cookies: dict[str, str] = cookies or {}
        self.__description: str = description
        self.__http2: bool = http2 if isinstance(http2, bool) else False
        self.__retry_times: int = retry_times if isinstance(retry_times, int) else 10
        self.__retry_interval: int = retry_interval if isinstance(retry_interval, int) else 5
        self.__retry_exit_code_range: int = retry_times if isinstance(retry_exit_code_range, list) else (i for i in
                                                                                                         range(200,
                                                                                                               300))
        self.__retry_exception_retry: int = retry_times if isinstance(retry_exception_retry, bool) else True
        self.__retry_check_handler: int = retry_times
        self.__session: Session = Session()
        if http2:
            scheme = urlparse(self.__host).scheme
            if scheme != _Constant.HTTPS:
                raise HttpException(f"http2 need https protocol, but found '{scheme}'")
            self.__session.mount(f"{_Constant.HTTPS}://", HTTP20Adapter())
        if file:
            path = Path(file)
            if not path.is_absolute():
                path = Path.cwd().joinpath(file)
            if not path.exists():
                raise RuntimeError(f"not found file: {path}")
            with open(path.absolute(), "r") as f:
                self.__server_list = json.load(f)

    @property
    def restful(self) -> RestFul:
        return self.__restful

    @property
    def check_status(self) -> bool:
        return self.__check_status

    @check_status.setter
    def check_status(self, value):
        if isinstance(value, bool):
            self.__check_status = value
        else:
            raise TypeError(f"Excepted type is 'bool', got a '{type(value).__name__}'")

    @property
    def encoding(self) -> str:
        return self.__encoding

    @encoding.setter
    def encoding(self, value):
        if issubclass(value_type := type(value), str):
            self.__encoding = value
        else:
            raise TypeError(f"Excepted type is 'str', got a '{value_type.__name__}'")

    @property
    def server_name(self) -> str:
        return self.__server_name

    @server_name.setter
    def server_name(self, value):
        if issubclass(value_type := type(value), str):
            self.__server_name = value
        else:
            raise TypeError(f"Excepted type is 'str', got a '{value_type.__name__}'")

    @property
    def server_list(self) -> list:
        return self.__server_list

    @server_list.setter
    def server_list(self, value):
        if issubclass(value_type := type(value), list):
            self.__server_list = value
        else:
            raise TypeError(f"Excepted type is 'str', got a '{value_type.__name__}'")

    @property
    def server(self) -> dict:
        return self.__server

    @server.setter
    def server(self, value):
        if issubclass(value_type := type(value), dict):
            self.__server = value
        else:
            raise TypeError(f"Excepted type is 'dict', got a '{value_type.__name__}'")

    @property
    def host(self) -> str:
        return self.__host

    @host.setter
    def host(self, value):
        if issubclass(value_type := type(value), str):
            self.__host = value
        else:
            raise TypeError(f"Excepted type is 'str', got a '{value_type.__name__}'")

    @property
    def description(self) -> str:
        return self.__host

    @description.setter
    def description(self, value):
        if issubclass(value_type := type(value), str):
            self.__description = value
        else:
            raise TypeError(f"Excepted type is 'str', got a '{value_type.__name__}'")

    def soul(self, rest: 'Rest'):
        """
        Copy the properties of rest now to the current instance.
        The action of copying is a transient operation,
        and subsequent property changes at rest will not affect the object
        """
        self.__restful, self.__check_status, self.__encoding, self.__server_name, self.__server_list, self.__host, \
            self.__description, self.__http2, self.__session = rest.restful, rest.check_status, rest.encoding, \
            rest.server_name, rest.server_list, rest.host, rest.description, rest.__http2, rest.__session

    def retry(self, times: int = None, interval: int = None, exit_code_range: list = None, exception_retry: bool = None,
              check_handler: Callable[[Any], bool] = None) -> T:
        """
        if http request fail or exception, will retry.
        :param check_handler: This parameter is a callback function, if the return value is a pure body,
        it will determine whether to continue (make) the retry by checking the key of the body
        :param times: Number of retries
        :param interval: Retry interval
        :param exit_code_range: The expected HTTP status,
        if the response status code of the HTTP request is within this range, will exit the retry. The range is closed.
        default value [200, 299].
        :param exception_retry: Whether to retry when an exception occurs. True will try again

        If all of the above parameters are provided, the default values are used.

        Example:
            class Api:
                rest = Rest("rest.json", host="http://localhost:8080", description="demo domain")

                @rest.retry(times=2)
                @rest.get(description="打印hello")
                def test_case2(self,  response) -> RestResponse:
                    return response
        """

        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                times_ = times if isinstance(times, int) else self.__retry_times
                interval_ = interval if isinstance(interval, int) else self.__retry_interval
                exit_code_range_ = exit_code_range if isinstance(exit_code_range,
                                                                 list) else self.__retry_exit_code_range
                exception_retry_ = exception_retry if isinstance(exception_retry,
                                                                 bool) else self.__retry_exception_retry
                check_handler_ = check_handler if callable(check_handler) else self.__retry_check_handler

                def default_check_body_call_back(res) -> bool:
                    return res and "status" in res and resp["status"] in exit_code_range_

                check_handler_ = check_handler_ if callable(check_handler_) else default_check_body_call_back
                number_ = times_ + 1
                for i in range(1, times_ + 2):
                    # noinspection PyBroadException
                    try:
                        resp = func(*args, **kwargs)
                        #
                        if isinstance(resp, Response):
                            if resp.status_code in exit_code_range_:
                                return resp
                        # Compatible with only_body parameters
                        elif isinstance(resp, dict or list):
                            if check_handler_(resp):
                                return resp
                        if i == number_:
                            break
                        else:
                            _LOGGER.log(level=30, msg=f"http request retry times: {i}", stacklevel=3)
                            sleep(interval_)
                    except BaseException as e:
                        if isinstance(e, RestInternalException):
                            if exception_retry_:
                                if i == number_:
                                    break
                                else:
                                    _LOGGER.log(level=30, msg=f"http request retry times: {i}", stacklevel=3)
                                    sleep(interval_)
                            else:
                                return
                        else:
                            raise e

            return __wrapper

        return __inner

    def request(self, api_name: str = None, server_name: str = None, host: str = None, api: str = None,
                method: HttpMethod or str = None, allow_redirection: bool = RestConfig.allow_redirection,
                headers: dict = None, check_status: bool = RestConfig.check_status,
                encoding: str = RestConfig.encoding, description: str = None, restful: RestFul = None) -> T:
        """
        http  request, need to specify the request method.
        Configure the interface information
        Important: requests arguments must be keyword arguments
        :param description: api's description info
        :param encoding: parse response's text or content encode
        :param check_status: check http response status, default false
        :param api_name: Specify the API name, if empty while use function name as api name
        :param server_name: service name, which overrides the server_name of the instance.
                            If it is blank and the instance server_name is also blank,
                            the class name is used as the server name
        :param host: interface domain name, which is used first
        :param api: service http interface, which takes precedence over this parameter when specified
        :param method: interface request method, which is used in preference after specified
        :param allow_redirection: Whether to automatically redirect, the default is
        :param headers: custom http request header, if allow_redirection parameter is included,
        the allow_redirection in the header takes precedence
        :param restful: if it is a restful-style URL, it is used to replace the keywords in the URL,
        and if the keyword is missing, KeyError will be thrown

        The parameters of the func only need a 'response', others, such as params, data, etc.,
        can be specified directly in the argument as keyword arguments.
        Keyword parameter restrictions only support the following parameters,include "params", "data", "json",
        "headers", "cookies", "files", "auth", "timeout", "allow_redirects", "proxies", "verify", "stream", "cert",
        "stream", "hooks".
        if requests module have been added new parameters, Options object is recommended because it is not limited by
        the parameters above.
        usage:
            normal use:
                class User:
                    rest = Rest(host)

                    @rest.get(api="/get_user", method=Method.GET)
                    def get_info(self, response):
                        return response
                user = User()


            type_reference:
                @EntityType()
                class Data(Entity):
                    id: list[str]
                    OK: str


                class User:
                    rest = Rest(host)

                    @rest.get(api="/get_user", method=Method.GET, type_reference=Data)
                    def get_info(self, response):
                        return response
                user = User()
                print(user.get_info())  # Data(id=[1], OK='200')






            # There is no such parameter in the formal parameter, but we can still pass the parameter using the
            specified keyword parameter.
            user.get_info(params={}, data={}) equivalent to user.get_info(opts=RestOptions(params={}, data={}))
            We recommend that you use the Options object.
            In the future, RestOptions will be forced to pass requests parameters.
            That is, only the 'user.get_info(opts=RestOptions(params={}, data={}))' model will be supported in the
            future.
        """

        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                self.__request(func=func, kwargs=kwargs, api_name=api_name, server_name=server_name, host=host, api=api,
                               method=method, allow_redirection=allow_redirection, headers=headers,
                               check_status=check_status, encoding=encoding, description=description, restful=restful)
                return func(*args, **kwargs)

            return __wrapper

        return __inner

    def get(self, api_name: str = None, server_name: str = None, host: str = None, api: str = None,
            allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
            check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding, description: str = None,
            restful: RestFul = None) -> T:
        """
        http get request method
        Refer to request().
        usage:
            class User:
                rest = Rest(host)

                @rest.get(api="/get_user")
                def get_info(self, response):
                    return response
            user = User()

            # There is no such parameter in the formal parameter, but we can still pass the parameter using the
            specified keyword parameter.
            user.get_info(params={}, data={}) equivalent to user.get_info(opts=RestOptions(params={}, data={}))
            We recommend that you use the Options object.
            In the future, RestOptions will be forced to pass requests parameters.
            That is, only the 'user.get_info(opts=RestOptions(params={}, data={}))' model will be supported in the
            future.
        """

        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                self.__request(func=func, kwargs=kwargs, api_name=api_name, server_name=server_name, host=host, api=api,
                               method=HttpMethod.GET, allow_redirection=allow_redirection, headers=headers,
                               check_status=check_status, encoding=encoding, description=description, restful=restful)
                return func(*args, **kwargs)

            return __wrapper

        return __inner

    def post(self, api_name: str = None, server_name: str = None, host: str = None, api: str = None,
             allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
             check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding,
             description: str = None, restful: RestFul = None) -> T:
        """
        http POST request method.
        Refer to request().
        usage:
            class User:
                rest = Rest(host)

                @rest.post(api="/get_user")
                def get_info(self, response):
                    return response
            user = User()

            # There is no such parameter in the formal parameter, but we can still pass the parameter using the
            specified keyword parameter.
            user.get_info(params={}, data={}) equivalent to user.get_info(opts=RestOptions(params={}, data={}))
            We recommend that you use the Options object.
            In the future, RestOptions will be forced to pass requests parameters.
            That is, only the 'user.get_info(opts=RestOptions(params={}, data={}))' model will be supported in the
            future.
        """

        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                self.__request(func=func, kwargs=kwargs, api_name=api_name, server_name=server_name, host=host, api=api,
                               method=HttpMethod.POST, allow_redirection=allow_redirection, headers=headers,
                               check_status=check_status, encoding=encoding, description=description, restful=restful)
                return func(*args, **kwargs)

            return __wrapper

        return __inner

    def put(self, api_name: str = None, server_name: str = None, host: str = None, api: str = None,
            allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
            check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding, description: str = None,
            restful: RestFul = None) -> T:
        """
        http PUT request method.
        Refer to request().
        usage:
            class User:
                rest = Rest(host)

                @rest.put(api="/get_user")
                def get_info(self, response):
                    return response
            user = User()

            # There is no such parameter in the formal parameter, but we can still pass the parameter using the
            specified keyword parameter.
            user.get_info(params={}, data={}) equivalent to user.get_info(opts=RestOptions(params={}, data={}))
            We recommend that you use the Options object.
            In the future, RestOptions will be forced to pass requests parameters.
            That is, only the 'user.get_info(opts=RestOptions(params={}, data={}))' model will be supported in the
            future.
        """

        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                self.__request(func=func, kwargs=kwargs, api_name=api_name, server_name=server_name, host=host, api=api,
                               method=HttpMethod.PUT, allow_redirection=allow_redirection, headers=headers,
                               check_status=check_status, encoding=encoding, description=description, restful=restful)
                return func(*args, **kwargs)

            return __wrapper

        return __inner

    def delete(self, api_name: str = None, server_name: str = None, host: str = None, api: str = None,
               allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
               check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding,
               description: str = None, restful: RestFul = None) -> T:
        """
        http DELETE request method
        Refer to request().
        usage:
            class User:
                rest = Rest(host)

                @rest.delete(api="/get_user")
                def get_info(self, response):
                    return response
            user = User()

            # There is no such parameter in the formal parameter, but we can still pass the parameter using the
            specified keyword parameter.
            user.get_info(params={}, data={}) equivalent to user.get_info(opts=RestOptions(params={}, data={}))
            We recommend that you use the Options object.
            In the future, RestOptions will be forced to pass requests parameters.
            That is, only the 'user.get_info(opts=RestOptions(params={}, data={}))' model will be supported in the
            future.
        """

        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                self.__request(func=func, kwargs=kwargs, api_name=api_name, server_name=server_name, host=host, api=api,
                               method=HttpMethod.DELETE, allow_redirection=allow_redirection, headers=headers,
                               check_status=check_status, encoding=encoding, description=description, restful=restful)
                return func(*args, **kwargs)

            return __wrapper

        return __inner

    def patch(self, api_name: str = None, server_name: str = None, host: str = None, api: str = None,
              allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
              check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding,
              description: str = None, restful: RestFul = None) -> T:
        """
        http PATCH request method
        Refer to request().
        usage:
            class User:
                rest = Rest(host)

                @rest.patch(api="/get_user")
                def get_info(self, response):
                    return response
            user = User()

            # There is no such parameter in the formal parameter, but we can still pass the parameter using the
            specified keyword parameter.
            user.get_info(params={}, data={}) equivalent to user.get_info(opts=RestOptions(params={}, data={}))
            We recommend that you use the Options object.
            In the future, RestOptions will be forced to pass requests parameters.
            That is, only the 'user.get_info(opts=RestOptions(params={}, data={}))' model will be supported in the
            future.
        """

        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                self.__request(func=func, kwargs=kwargs, api_name=api_name, server_name=server_name, host=host, api=api,
                               method=HttpMethod.PATCH, allow_redirection=allow_redirection, headers=headers,
                               check_status=check_status, encoding=encoding, description=description, restful=restful)
                return func(*args, **kwargs)

            return __wrapper

        return __inner

    def head(self, api_name: str = None, server_name: str = None, host: str = None, api: str = None,
             allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
             check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding,
             description: str = None, restful: RestFul = None) -> T:
        """
        http HEAD request method
        Refer to request().
        usage:
            class User:
                rest = Rest(host)

                @rest.head(api="/get_user")
                def get_info(self, response):
                    return response
            user = User()

            # There is no such parameter in the formal parameter, but we can still pass the parameter using the
            specified keyword parameter.
            user.get_info(params={}, data={}) equivalent to user.get_info(opts=RestOptions(params={}, data={}))
            We recommend that you use the Options object.
            In the future, RestOptions will be forced to pass requests parameters.
            That is, only the 'user.get_info(opts=RestOptions(params={}, data={}))' model will be supported in the
            future.
        """

        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                self.__request(func=func, kwargs=kwargs, api_name=api_name, server_name=server_name, host=host, api=api,
                               method=HttpMethod.HEAD, allow_redirection=allow_redirection, headers=headers,
                               check_status=check_status, encoding=encoding, description=description, restful=restful)
                return func(*args, **kwargs)

            return __wrapper

        return __inner

    def options(self, api_name: str = None, server_name: str = None, host: str = None, api: str = None,
                allow_redirection: bool = RestConfig.allow_redirection, headers: dict = None,
                check_status: bool = RestConfig.check_status, encoding: str = RestConfig.encoding,
                description: str = None, restful: RestFul = None) -> T:
        """
        http OPTIONS request method
        Refer to request().
        usage:
            class User:
                rest = Rest(host)

                @rest.options(api="/get_user")
                def get_info(self, response):
                    return response
            user = User()

            # There is no such parameter in the formal parameter, but we can still pass the parameter using the
            specified keyword parameter.
            user.get_info(params={}, data={}) equivalent to user.get_info(opts=RestOptions(params={}, data={}))
            We recommend that you use the Options object.
            In the future, RestOptions will be forced to pass requests parameters.
            That is, only the 'user.get_info(opts=RestOptions(params={}, data={}))' model will be supported in the
            future.
        """

        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                self.__request(func=func, kwargs=kwargs, api_name=api_name, server_name=server_name, host=host, api=api,
                               method=HttpMethod.OPTIONS, allow_redirection=allow_redirection, headers=headers,
                               check_status=check_status, encoding=encoding, description=description, restful=restful)
                return func(*args, **kwargs)

            return __wrapper

        return __inner

    def __request(self, func: callable, kwargs: dict, api_name: str = None, server_name: str = None, host: str = None,
                  api: str = None, method: HttpMethod or str = None, allow_redirection: bool = True,
                  headers: dict = None, check_status: bool = None, encoding: str = None, description: str = None,
                  restful: RestFul = None):
        """
        Configure the interface information
        Important: requests arguments must be keyword arguments
        :param description: api's description info
        :param encoding: parse response's text or content encode
        :param check_status: check http response status, default false
        :param api_name: Specify the API name, if empty while use function name as api name
        :param server_name: service name, which overrides the server_name of the instance.
                            If it is blank and the instance server_name is also blank,
                            the class name is used as the server name
        :param host: interface domain name, which is used first
        :param api: service http interface, which takes precedence over this parameter when specified
        :param method: interface request method, which is used in preference after specified
        :param allow_redirection: Whether to automatically redirect, the default is
        :param headers: custom http request header, if allow_redirection parameter is included,
        the allow_redirection in the header takes precedence

        The parameters of the func only need a 'response', others, such as params, data, etc.,
        can be specified directly in the argument as keyword arguments.
        Keyword parameter restrictions only support the following parameters,include "params", "data", "json",
        "headers", "cookies", "files", "auth", "timeout", "allow_redirects", "proxies", "verify", "stream", "cert",
        "stream", "hooks".
        if requests module have been added new parameters, Options object is recommended because it is not limited by
        the parameters above.
        usage:
            class User:
                rest = Rest(host)

                def get_info(self, response):
                    return response
            user = User()
            user.get_info()

            # There is no such parameter in the formal parameter, but we can still pass the parameter using
            the specified keyword parameter.
            user.get_info(params={}, data={}) equivalent to user.get_info(opts=RestOptions(params={}, data={}))
            We recommend that you use the Options object.
            In the future, RestOptions will be forced to pass requests parameters.
            That is, only the 'user.get_info(opts=RestOptions(params={}, data={}))' model
            will be supported in the future.
        """
        spec = getfullargspec(func)
        log_builder = StringBuilder()
        self.__build_log_message(log_builder, f"{'Http Request Start'.center(41, '*')}")
        if "response" not in spec.args and "response" not in spec.kwonlyargs:
            raise HttpException(f"function {func.__name__} need 'response' args, ex: {func.__name__}(response) "
                                f"or {func.__name__}(response=None)")
        server_name_: str = self.__server_name_handler(server_name, func)
        api_name_: str = self.__api_name_handler(api_name, func)
        server_dict: dict = self.__server_dict_handler(server_name_)
        server_description = self.__server_desc_handler(self.__description, server_dict)
        host_: str = self.__host_handler(host, server_dict)
        api_info: dict = self.__api_handler(server_dict, api_name_)
        optional_args: dict = self.__optional_args_handler(api_info, kwargs)
        optional_args[_Constant.ALLOW_REDIRECTS] = allow_redirection
        api_: str = ObjectsUtils.none_of_default(api_info.get(_Constant.API_PATH), api)
        ObjectsUtils.check_non_none(api_)
        api_description = self.__api_desc_handler(description, server_dict, api_name_, _Constant.DESC)
        method_: str = api_info.get(_Constant.HTTP_METHOD, self.__get_request_method(method))
        ObjectsUtils.check_non_none(HttpMethod.get_by_value(method_.upper()))
        headers_: dict = api_info.get(_Constant.HEADERS, {})
        self.__header_handler(optional_args, method_.upper(), headers_, headers)
        url: str = urljoin(host_, api_)
        check_status_: bool = self.__check_status if not check_status else check_status
        encoding_: str = self.__encoding if not encoding else encoding
        optional_args_tmp = {}
        for k, v in deepcopy(optional_args).items():
            if k in _OPTIONAL_ARGS_KEYS and v:
                optional_args_tmp[k] = v

        resp = None
        rest_resp = RestResponse(None)
        url: str = url.format(**self.__restful_handler(restful, optional_args.get(_Constant.RESTFUL)))
        # noinspection PyBroadException
        try:
            resp: Response or None = self.__action(method_.lower(), url, **optional_args_tmp)
            if check_status_:
                if 200 > resp.status_code or resp.status_code >= 300:
                    _LOGGER.log(level=40, msg=f"check http status code is not success: {resp.status_code}",
                                stacklevel=4)
                    raise HttpException(f"http status code is not success: {resp.status_code}")

            rest_resp = RestResponse(resp)

        except BaseException as e:
            e.__init__(f"An exception occurred during the http request process: url is {host_}{api_}")
            _LOGGER.log(level=40, msg=f"An exception occurred when a request was sent without a response:\n"
                                      f"{traceback.format_exc()}", stacklevel=4)
            raise RestInternalException(e)
        finally:
            kwargs[_Constant.RESPONSE] = rest_resp
            url_ = url if not resp else resp.url
            arguments = "".join([f'\t{k.ljust(20, " ")} => {v}\n' for k, v in optional_args_tmp.items()])
            content = rest_resp.content.decode(encoding_)[:10240]
            content = content if content.endswith("\n") else f"{content}\n"
            self.__build_log_message(log_builder,
                                     f"[Server     Description]: {server_description}\n"
                                     f"[Api        Description]: {api_description}\n"
                                     f"[Request    Information]: \n"
                                     f"\t{'url'.ljust(20, ' ')} => {url_}\n"
                                     f"\t{'method'.ljust(20, ' ')} => {method_.upper()}\n"
                                     f"{arguments}"
                                     f"[Response   Information]: \n"
                                     f"\t{'http status'.ljust(20, ' ')} => {rest_resp.code}\n"
                                     f"\t# if response content lengths longer than 4096 will omit subsequent "
                                     f"characters.\n"
                                     f"\t{'resp content'.ljust(20, ' ')} => {content}"
                                     f"\t{'headers'.ljust(20, ' ')} => {rest_resp.headers}")
            self.__build_log_message(log_builder, f"{'Http Request End'.center(43, '*')}")
            _LOGGER.log(level=20, msg=log_builder, stacklevel=2)

    def __restful_handler(self, restful, func_restful_args) -> dict:
        rest_ful = RestFul()
        rest_ful.update(self.__restful)
        rest_ful.update(restful)
        rest_ful.update(func_restful_args)
        return rest_ful.to_dict()

    def __server_dict_handler(self, name: str) -> dict:
        if name in self.server:
            return self.server.get(name)
        if self.__server_list:
            for server in self.__server_list:
                if server.get(_Constant.SERVER_NAME) == name:
                    self.server[name] = server
                    return server
        return {}

    def __host_handler(self, host: str, server_dict: dict) -> str:
        host_: str = host
        if not host_:
            host_: str = self.__host
        if not host_:
            host_: str = server_dict.get(_Constant.SERVER_HOST)
        if not _HTTP_RE.match(host_):
            raise RuntimeError(f"invalid host: {host_}")
        return host_

    def __server_name_handler(self, server_name: str, func: callable) -> str:
        if isinstance(server_name, str) and server_name.strip() != "":
            return server_name
        if isinstance(self.__server_name, str) and self.__server_name.strip() != "":
            return self.__server_name
        return func.__qualname__.split(".")[0]

    @staticmethod
    def __get_request_method(method: HttpMethod or str) -> str:
        if isinstance(method, HttpMethod):
            return method.value
        elif isinstance(method, str):
            return HttpMethod.get_by_value(method, HttpMethod.GET).value
        else:
            return HttpMethod.GET.value

    def __action(self, http_method: str, url: str, **kwargs) -> Response:
        kwargs["url"] = url
        action = getattr(self.__session, http_method, None)
        if action:
            try:
                return action(**kwargs)
            except BaseException as e:

                raise e
                # raise HttpException(f"http request happened exception: {str(e)}")
        else:
            raise HttpException(f"unknown http method '{http_method}'")

    @staticmethod
    def __api_handler(server_dict: dict, api_name) -> T:
        """
        get api info from config
        """
        if "apis" in server_dict:
            api_list: list[dict] = server_dict.get("apis")
            if issubclass(type(api_list), list):
                for api in api_list:
                    if isinstance(api, dict) and api.get("apiName") == api_name:
                        return api
        return {}

    def __header_handler(self, all_params: dict, method: str = HttpMethod.GET.value,
                         headers_by_config: dict = None, headers_by_kwargs: dict = None):
        headers_: dict = all_params.get("headers", {})
        if method == HttpMethod.POST.value or method == HttpMethod.PUT.value or method == HttpMethod.DELETE.value:
            content_type = _Constant.CONTENT_TYPE_JSON
        else:
            content_type = _Constant.CONTENT_TYPE_DEFAULT

        if not headers_:
            headers_.update(self.__headers)
            headers_[_Constant.CONTENT_TYPE] = content_type
        else:
            if not self.__header_has_key(headers_, _Constant.CONTENT_TYPE, True):
                headers_[_Constant.CONTENT_TYPE] = content_type
        if not self.__header_has_key(headers_, "cookie", True) and not self.__header_has_key(headers_, "cookies", True):
            if self.__cookies:
                headers_["Cookie"] = ";".join(f"{k}={v}" for k, v in self.__cookies.items())
        if isinstance(headers_by_config, dict):
            headers_.update(headers_by_config)
        if issubclass(type(headers_by_kwargs), dict):
            headers_.update(headers_by_kwargs)
        all_params[_Constant.HEADERS] = headers_

    @staticmethod
    def __header_has_key(headers: dict, verify_key: str, ignore_case: bool = False) -> bool:
        if not headers:
            return False
        if ignore_case:
            tmp_verify_key = verify_key.lower()
        else:
            tmp_verify_key = verify_key
        for k in headers.keys():
            if ignore_case:
                key = k.lower()
            else:
                key = k
            if tmp_verify_key == key:
                return True
            else:
                continue
        else:
            return False

    @staticmethod
    def __optional_args_handler(api_info: dict, kwargs: dict) -> dict:
        optional_args: dict = Dictionary()
        api_info_: dict = api_info if issubclass(type(api_info), dict) else {}
        for key in _OPTIONAL_ARGS_KEYS:
            if key in api_info_:
                optional_args[key] = api_info_.get(key)
        if optional_args:
            for k, v in deepcopy(optional_args).items():
                if not v:
                    del optional_args[k]
        if _Constant.OPTS in kwargs:
            options = kwargs.get(_Constant.OPTS)
            if options and isinstance(options, RestOptions):
                optional_args.update(options.opts_no_none)
                del kwargs[_Constant.OPTS]
        return optional_args

    @staticmethod
    def __api_name_handler(api_name: str, func: callable) -> str:
        if isinstance(api_name, str) and api_name.strip() != "":
            return api_name
        return func.__name__

    @staticmethod
    def __server_desc_handler(origin: str, server_dict: dict) -> str:
        desc: str = origin
        if not desc:
            desc: str = server_dict.get("desc")
        return desc

    @staticmethod
    def __api_desc_handler(default: T, server_dict: dict, api_name, key: str) -> T:
        default_: dict = default
        if not default_ and _Constant.APIS in server_dict:
            api_list: list[dict] = server_dict.get(_Constant.APIS)
            if not api_list:
                return default_
            for api in api_list:
                if isinstance(api, dict) and api.get(_Constant.API_NAME) == api_name:
                    return api.get(key)
        return default_

    @staticmethod
    def __build_log_message(origin: StringBuilder, msg: str):
        origin.append(f"\n{msg}\n")

    @staticmethod
    def bulk(content: str) -> dict:
        """
        Convert headers copied from the browser to dicts
        :param content: copied header from the browser
        :return: python dict object
        """
        tmp = {}
        if issubclass(type(content), str):
            for line in content.split("\n"):
                kvs = line.split(":")
                kv_len = len(kvs)
                if kv_len == 2:
                    tmp[StringUtils.trip(kvs[0])] = StringUtils.trip(kvs[1])
                elif kv_len == 1:
                    tmp[StringUtils.trip(kvs[0])] = ""
                elif len(kvs) == 3:
                    tmp[f":{StringUtils.trip(kvs[1])}"] = StringUtils.trip(kvs[kv_len - 1])
                else:
                    _LOGGER.warning(f"unknown header: '{line}'")
            return tmp
        else:
            return {"content": content}


__all__ = [Rest, RestFast, HttpMethod, RestOptions, RestFul, RestResponse]
