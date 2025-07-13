import json
import logging
import os
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Optional, Union
from urllib.parse import parse_qs

from requests import Response, Session
from requests.auth import HTTPBasicAuth

from ark_sdk_python.auth.identity.ark_identity_fqdn_resolver import ArkIdentityFQDNResolver
from ark_sdk_python.common import ArkKeyring, ArkSystemConfig, get_logger
from ark_sdk_python.common.ark_jwt_utils import ArkJWTUtils
from ark_sdk_python.common.env import DEPLOY_ENV, IDENTITY_ENV_URLS, AwsEnv
from ark_sdk_python.models import ArkAuthException, ArkProfile
from ark_sdk_python.models.auth import ArkAuthMethod, ArkToken, ArkTokenType


class ArkIdentityServiceUser:
    def __init__(
        self,
        username: str,
        token: str,
        app_name: str,
        identity_url: Optional[str] = None,
        env: Optional[AwsEnv] = None,
        logger: Optional[logging.Logger] = None,
        cache_authentication: bool = True,
        verify: Optional[Union[str, bool]] = None,
        load_cache: bool = False,
        cache_profile: Optional[ArkProfile] = None,
    ) -> None:
        self.__username = username
        self.__token = token
        self.__app_name = app_name
        self.__env = env or AwsEnv(os.getenv(DEPLOY_ENV, AwsEnv.PROD.value))
        self.__identity_url = identity_url or self.__resolve_fqdn_from_username()
        self.__logger = logger or get_logger(app=self.__class__.__name__)
        self.__keyring = ArkKeyring(self.__class__.__name__.lower()) if cache_authentication else None
        self.__cache_authentication = cache_authentication

        self.__session = Session()
        self.__session_token = None
        self.__session_exp = None
        self.__session.headers.update(ArkIdentityFQDNResolver.default_system_headers())
        if verify is None:
            if ArkSystemConfig.trusted_certificate() is not None:
                verify = ArkSystemConfig.trusted_certificate()
            else:
                verify = ArkSystemConfig.is_verifiying_certificates()
        self.__session.verify = verify
        if load_cache and cache_authentication and cache_profile:
            self.__load_cache(cache_profile)

    def __load_cache(self, profile: Optional[ArkProfile] = None) -> bool:
        if self.__keyring and profile:
            token = self.__keyring.load_token(profile, f'{self.__username}_identity_service_user')
            if token and token.username == self.__username:
                self.__session_token = token.token.get_secret_value()
                self.__session_exp = token.expires_in
                self.__session.headers.update({'Authorization': f'Bearer {self.__session_token}'})
                return True
        return False

    def __save_cache(self, profile: Optional[ArkProfile] = None) -> None:
        if self.__keyring and profile and self.__session_token:
            if not self.__session_exp:
                self.__session_exp = datetime.now() + timedelta(hours=4)
            self.__keyring.save_token(
                profile,
                ArkToken(
                    token=self.__session_token,
                    username=self.__username,
                    endpoint=self.__identity_url,
                    token_type=ArkTokenType.Internal,
                    auth_method=ArkAuthMethod.Other,
                    expires_in=self.__session_exp,
                ),
                f'{self.__username}_identity_service_user',
            )

    def __resolve_fqdn_from_username(self) -> str:
        tenant_suffix = self.__username[self.__username.index('@') :]
        return ArkIdentityFQDNResolver.resolve_tenant_fqdn_from_tenant_suffix(
            tenant_suffix=tenant_suffix, identity_env_url=IDENTITY_ENV_URLS[self.__env]
        )

    def auth_identity(self, profile: Optional[ArkProfile] = None, force: bool = False) -> None:
        """
        Authenticates to Identity with a service user.
        This method creates an auth token and authorizes to the service.

        Args:
            profile (Optional[ArkProfile]): Profile to be used to load from caching, if available
            force (bool): Determines whether to discard existing cache, defaults to `False`

        Raises:
            ArkAuthException: _description_
        """
        # Login to identity with the service service user
        self.__logger.info(f'Authenticating to service user via endpoint [{self.__identity_url}]')
        if self.__cache_authentication and not force and self.__load_cache(profile):
            # Check if expired
            if self.__session_exp.replace(tzinfo=None) > datetime.now():
                self.__logger.info('Loaded identity service user details from cache')
                return

        token_response: Response = self.__session.post(
            url=f'{self.__identity_url}/Oauth2/Token/{self.__app_name}',
            auth=HTTPBasicAuth(self.__username, self.__token),
            verify=True,
            data={'grant_type': 'client_credentials', 'scope': 'api'},
        )
        if token_response.status_code != HTTPStatus.OK:
            raise ArkAuthException('Failed logging in to identity service user')
        auth_result = json.loads(token_response.text)
        if 'access_token' not in auth_result.keys():
            raise ArkAuthException('Failed logging in to identity service user, access token not found')
        access_token = auth_result['access_token']

        # Authorize to the application with the service user
        params = {
            'client_id': self.__app_name,
            'response_type': 'id_token',
            'scope': 'openid profile api',
            'redirect_uri': 'https://cyberark.cloud/redirect',
        }
        self.__logger.info(f'Trying to request a platform authorization with params [{params}]')
        authorize_response = self.__session.get(
            url=f'{self.__identity_url}/OAuth2/Authorize/{self.__app_name}',
            headers={'Authorization': f'Bearer {access_token}'},
            params=params,
            allow_redirects=False,
        )
        if authorize_response.status_code != HTTPStatus.FOUND or 'Location' not in authorize_response.headers:
            raise ArkAuthException('Failed to authorize to application')
        # Parse the authorized token and return the session with it
        location_header_splitted = authorize_response.headers['Location'].split('#', 1)
        if len(location_header_splitted) != 2:
            raise ArkAuthException('Failed to parse location header to retrieve token from')
        parsed_query = parse_qs(location_header_splitted[1])
        if 'id_token' not in parsed_query or len(parsed_query['id_token']) != 1:
            raise ArkAuthException('Failed to parse id token from location header')
        self.__session_token = parsed_query['id_token'][0]
        self.__session.headers.update({'Authorization': f'Bearer {self.__session_token}', **ArkIdentityFQDNResolver.default_headers()})
        try:
            decoded_token = ArkJWTUtils.get_unverified_claims(self.__session_token)
            self.__session_exp = datetime.fromtimestamp(decoded_token['exp'])
        except Exception:
            self.__session_exp = datetime.now() + timedelta(hours=4)
        self.__logger.info(
            f'Created a service user session via endpoint [{self.__identity_url}] ' f'with user [{self.__username}] to platform'
        )
        if self.__cache_authentication:
            self.__save_cache(profile)

    @property
    def session(self) -> Session:
        return self.__session

    @property
    def session_exp(self) -> Optional[datetime]:
        return self.__session_exp

    @property
    def session_token(self) -> Optional[str]:
        return self.__session_token

    @property
    def identity_url(self) -> str:
        return self.__identity_url
