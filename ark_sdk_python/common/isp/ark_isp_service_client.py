# pylint: disable=unused-argument
import codecs
import os
import pickle
from typing import Callable, Optional
from urllib.parse import urlparse

from requests.cookies import RequestsCookieJar

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common.ark_client import ArkClient
from ark_sdk_python.common.env import ROOT_DOMAIN, AwsEnv
from ark_sdk_python.models import ArkException


class ArkISPServiceClient(ArkClient):
    def __init__(
        self,
        service_name: Optional[str] = None,
        tenant_subdomain: Optional[str] = None,
        base_tenant_url: Optional[str] = None,
        tenant_env: Optional[AwsEnv] = None,
        token: Optional[str] = None,
        auth_header_name: str = 'Authorization',
        seperator: str = '.',
        base_path: Optional[str] = None,
        cookie_jar: Optional[RequestsCookieJar] = None,
        refresh_connection_callback: Optional[Callable[['ArkClient'], None]] = None,
    ) -> None:
        self.__tenant_env = tenant_env or AwsEnv(os.environ.get('DEPLOY_ENV', AwsEnv.PROD.value))
        service_url = ArkISPServiceClient.service_url(service_name, tenant_subdomain, base_tenant_url, tenant_env, token, seperator)
        if base_path:
            service_url = f'{service_url}/{base_path}'
        super().__init__(
            base_url=service_url,
            token=token,
            auth_header_name=auth_header_name,
            cookie_jar=cookie_jar,
            refresh_connection_callback=refresh_connection_callback,
        )
        self.add_header('Origin', service_url)
        self.add_header('Referer', service_url)
        self.add_header('Content-Type', 'application/json')

    @staticmethod
    def service_url(
        service_name: Optional[str] = None,
        tenant_subdomain: Optional[str] = None,
        base_tenant_url: Optional[str] = None,
        tenant_env: Optional[AwsEnv] = None,
        token: Optional[str] = None,
        seperator: str = '.',
    ) -> str:
        from jose.jwt import get_unverified_claims

        tenant_env = tenant_env or AwsEnv(os.environ.get('DEPLOY_ENV', AwsEnv.PROD.value))
        platform_domain = ROOT_DOMAIN[tenant_env]
        tenant_chosen_subdomain = None
        if token:
            subdomain = get_unverified_claims(token).get('subdomain', None)
            if subdomain:
                tenant_chosen_subdomain = subdomain
            platform_token_domain = get_unverified_claims(token).get('platform_domain', None)
            if platform_token_domain:
                platform_domain = platform_token_domain
                tenant_env = list(filter(lambda e: ROOT_DOMAIN[e] == platform_domain, ROOT_DOMAIN.keys()))
        if not tenant_chosen_subdomain and tenant_subdomain:
            tenant_chosen_subdomain = tenant_subdomain
        if not tenant_chosen_subdomain and base_tenant_url:
            if not base_tenant_url.startswith('https://'):
                base_tenant_url = f'https://{base_tenant_url}'
            parsed_url = urlparse(base_tenant_url)
            tenant_chosen_subdomain = parsed_url.netloc.split('.', 1)[0]
        if not tenant_chosen_subdomain:
            unique_name = get_unverified_claims(token).get('unique_name', None)
            if unique_name:
                full_domain = unique_name.split('@', 1)
                if len(full_domain) > 1:
                    full_domain = full_domain[1]
                    for env, dom in ROOT_DOMAIN.items():
                        if dom in full_domain:
                            tenant_chosen_subdomain = full_domain.split('.', 1)[0]
                            platform_domain = dom
                            tenant_env = env
                            break
        if not tenant_chosen_subdomain:
            raise ArkException('Failed to resolve tenant subdomain')
        if service_name:
            base_url = f'https://{tenant_chosen_subdomain}{seperator}{service_name}.{platform_domain}'
        else:
            base_url = f'https://{tenant_chosen_subdomain}.{platform_domain}'
        return base_url

    @staticmethod
    def from_isp_auth(
        isp_auth: ArkISPAuth,
        service_name: Optional[str] = None,
        seperator: str = '.',
    ) -> 'ArkISPServiceClient':
        tenant_env = None
        base_tenant_url = None
        if isp_auth.token.username:
            for env, domain in ROOT_DOMAIN.items():
                if domain in isp_auth.token.username and '@' in isp_auth.token.username:
                    base_tenant_url = isp_auth.token.username.split('@')[1]
                    tenant_env = env
                    break
        if not tenant_env and 'env' in isp_auth.token.metadata:
            tenant_env = AwsEnv(isp_auth.token.metadata['env'])
        if not tenant_env:
            tenant_env = AwsEnv(os.environ.get('DEPLOY_ENV', AwsEnv.PROD.value))
        return ArkISPServiceClient(
            service_name=service_name,
            base_tenant_url=base_tenant_url,
            tenant_env=tenant_env,
            token=isp_auth.token.token.get_secret_value(),
            seperator=seperator,
            cookie_jar=(
                pickle.loads(codecs.decode(isp_auth.token.metadata['cookies'].encode(), "base64"))
                if 'cookies' in isp_auth.token.metadata
                else None
            ),
            refresh_connection_callback=ArkISPServiceClient.refresh_client,
        )

    @staticmethod
    def refresh_client(client: 'ArkISPServiceClient', isp_auth: ArkISPAuth) -> None:
        token = isp_auth.load_authentication(isp_auth.active_profile, True)
        if token:
            client.update_token(token.token.get_secret_value())
            client.update_cookies(
                cookie_jar=(
                    pickle.loads(codecs.decode(token.metadata['cookies'].encode(), "base64")) if 'cookies' in token.metadata else None
                )
            )

    @property
    def tenant_env(self) -> AwsEnv:
        return self.__tenant_env

    @property
    def tenant_id(self) -> str:
        if self.session_token:
            from jose.jwt import get_unverified_claims

            return get_unverified_claims(self.session_token)['tenant_id']
        raise ArkException('Failed to retrieve tenant id')
