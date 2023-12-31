import socket
from base64 import b64decode
from typing import Callable, Dict, List, Optional, Tuple, Union

import requests.packages.urllib3.util.connection as urllib3_cn  # pylint: disable=import-error
from requests import Response, Session
from requests.cookies import RequestsCookieJar

from ark_sdk_python.common.ark_system_config import ArkSystemConfig


def allowed_gai_family():
    return socket.AF_INET


urllib3_cn.allowed_gai_family = allowed_gai_family


class ArkClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        token_type: str = 'Bearer',
        cookies: Optional[List] = None,
        auth_header_name: str = 'Authorization',
        auth: Optional[Tuple[str, str]] = None,
        cookie_jar: Optional[RequestsCookieJar] = None,
        verify: Optional[Union[str, bool]] = None,
        refresh_connection_callback: Optional[Callable[['ArkClient'], None]] = None,
    ) -> None:
        from fake_useragent import UserAgent

        self.__session = Session()
        self.__base_url = base_url
        self.__token = token
        self.__token_type = token_type
        self.__auth_header_name = auth_header_name
        self.__refresh_connection_callback = refresh_connection_callback
        if self.__base_url and not self.__base_url.startswith('https://'):
            self.__base_url = f'https://{self.__base_url}'
        if auth:
            self.__session.auth = auth
        self.update_token(token)
        self.update_cookies(cookies, cookie_jar)
        if verify is None:
            if ArkSystemConfig.trusted_certificate() is not None:
                verify = ArkSystemConfig.trusted_certificate()
            else:
                verify = ArkSystemConfig.is_verifiying_certificates()
        self.__session.verify = verify
        self.__session.headers['User-Agent'] = UserAgent(browsers=['chrome']).googlechrome

    @property
    def base_url(self) -> Optional[str]:
        return self.__base_url

    @property
    def session(self) -> Session:
        return self.__session

    @property
    def session_token(self) -> Optional[str]:
        return self.__token

    @property
    def refresh_connection_callback(self) -> Optional[Callable[['ArkClient'], None]]:
        return self.__refresh_connection_callback

    def add_header(self, key: str, value: str) -> None:
        self.__session.headers.update({key: value})

    def add_headers(self, headers: Dict[str, str]) -> None:
        self.__session.headers.update(headers)

    def add_cookie(self, key: str, value: str) -> None:
        self.__session.cookies[key] = value

    def generic_http_method_request(self, method: str, route: str, **kwargs) -> Response:
        url = route
        if self.__base_url:
            url = f'{self.__base_url}'
            if route and route != '':
                if self.__base_url.endswith('/') or route.startswith('/'):
                    url = f'{self.__base_url}{route}'
                else:
                    url = f'{self.__base_url}/{route}'
        http_method = getattr(self.__session, method)
        response: Response = http_method(url, **kwargs)
        return response

    def get(self, route: str, **kwargs) -> Response:
        """
        Performs a GET request with the session details and given headers and tokens.

        Args:
            route (str): _description_

        Returns:
            Response: _description_
        """
        return self.generic_http_method_request('get', route, **kwargs)

    def post(self, route: str, **kwargs) -> Response:
        """
        Performs a POST request with the session details and given headers and tokens.

        Args:
            route (str): _description_

        Returns:
            Response: _description_
        """
        return self.generic_http_method_request('post', route, **kwargs)

    def put(self, route: str, **kwargs) -> Response:
        """
        Performs a PUT request with the session details and given headers and tokens.

        Args:
            route (str): _description_

        Returns:
            Response: _description_
        """
        return self.generic_http_method_request('put', route, **kwargs)

    def delete(self, route: str, **kwargs) -> Response:
        """
        Performs a DELETE request with the session details and given headers and tokens.

        Args:
            route (str): _description_

        Returns:
            Response: _description_
        """
        return self.generic_http_method_request('delete', route, **kwargs)

    def patch(self, route: str, **kwargs) -> Response:
        """
        Performs a PATCH request with the session details and given headers and tokens.

        Args:
            route (str): _description_

        Returns:
            Response: _description_
        """
        return self.generic_http_method_request('patch', route, **kwargs)

    def options(self, route: str, **kwargs) -> Response:
        """
        Performs a OPTIONS request with the session details and given headers and tokens.

        Args:
            route (str): _description_

        Returns:
            Response: _description_
        """
        return self.generic_http_method_request('options', route, **kwargs)

    def update_token(self, token: Optional[str] = None) -> None:
        """
        Updates a session token.

        Args:
            token (Optional[str], optional): _description_. Defaults to None.
        """
        self.__token = token
        if token:
            if self.__token_type == 'Basic':
                user, password = b64decode(token.encode('ascii')).decode('ascii').split(':')
                self.__session.auth = (user, password)
            else:
                if len(self.__token_type) == 0:
                    self.__session.headers.update({self.__auth_header_name: f'{self.__token}'})
                else:
                    self.__session.headers.update({self.__auth_header_name: f'{self.__token_type} {self.__token}'})

    def update_cookies(self, cookies: Optional[List] = None, cookie_jar: Optional[RequestsCookieJar] = None) -> None:
        """
        Updates session cookies.

        Args:
            cookies (Optional[List], optional): _description_. Defaults to None.
            cookie_jar (Optional[RequestsCookieJar], optional): _description_. Defaults to None.
        """
        if cookies:
            for c in cookies:
                self.__session.cookies.set_cookie(c)
        if cookie_jar:
            self.__session.cookies.update(cookie_jar)
