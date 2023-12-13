import os
from http import HTTPStatus
from typing import Dict, Final, Optional

from cachetools import LRUCache, cached
from pydantic import ValidationError
from requests import Session

from ark_sdk_python.common.env import IDENTITY_ENV_URLS, ROOT_DOMAIN, AwsEnv
from ark_sdk_python.models import ArkException
from ark_sdk_python.models.common.identity import TenantFqdnResponse
from ark_sdk_python.models.common.isp import IdentityEndpointResponse


class ArkIdentityFQDNResolver:
    __DISCOVERY_SERVICE_DOMAIN_NAME: Final[str] = 'platform-discovery'
    __DISCOVERY_TIMEOUT: Final[int] = 30

    @staticmethod
    @cached(cache=LRUCache(maxsize=1024))
    def default_headers() -> Dict[str, str]:
        from fake_useragent import UserAgent

        return {
            'Content-Type': 'application/json',
            'X-IDAP-NATIVE-CLIENT': 'true',
            'User-Agent': UserAgent(browsers=['chrome']).chrome,
            'OobIdPAuth': 'true',
        }

    @staticmethod
    @cached(cache=LRUCache(maxsize=1024))
    def default_system_headers() -> Dict[str, str]:
        from fake_useragent import UserAgent

        return {'X-IDAP-NATIVE-CLIENT': 'true', 'User-Agent': UserAgent(browsers=['chrome']).chrome}

    @staticmethod
    @cached(cache=LRUCache(maxsize=1024))
    def resolve_tenant_fqdn_from_tenant_subdomain(tenant_subdomain: str, env: AwsEnv) -> str:
        """
        Resolve the tenant FQDN url from platform discovery by its tenant subdomain.
        This is based on the environment that currently being worked on and given as an input

        Args:
            tenant_subdomain (str): the tenant subdomain, e.g. 'mytenant'
            env (AwsEnv): The environment to try and find the tenant on

        Raises:
            ArkException: In case of error, or tenant username prefix was not found in identity environment

        Returns:
            str: result of the platform discovery request to get the tenant FQDN
        """
        platform_discovery_url = f'https://{ArkIdentityFQDNResolver.__DISCOVERY_SERVICE_DOMAIN_NAME}.{ROOT_DOMAIN[env]}'
        session = Session()
        response = session.get(
            f'{platform_discovery_url}/api/identity-endpoint/{tenant_subdomain}',
            headers={'Content-Type': 'application/json'},
            timeout=ArkIdentityFQDNResolver.__DISCOVERY_TIMEOUT,
        )
        try:
            if response.status_code == HTTPStatus.OK:
                parsed_response: IdentityEndpointResponse = IdentityEndpointResponse.parse_raw(response.text)
                return str(parsed_response.endpoint)
        except (ValidationError, TypeError) as ex:
            raise ArkException('Getting tenant FQDN failed from platform discovery to be parsed / validated') from ex
        raise ArkException(f'Getting tenant FQDN failed from platform discovery [{response.status_code}] - [{response.text}]')

    @staticmethod
    @cached(cache=LRUCache(maxsize=1024))
    def resolve_tenant_fqdn_from_tenant_suffix(tenant_suffix: str, identity_env_url: Optional[str] = None) -> str:
        """
        Resolve the tenant FQDN url in identity. By default it gets identity address according
        to the current environment mapping (see get_identity_env_url()), but it can get it as argument (identity_env_url)

        Args:
            tenant_suffix (str): the tenant url suffix, e.g. '@tenant-a-527.shell.cyberark.cloud'
            identity_env_url (str, optional): If specified, used as the identity pod0 url. Defaults to None (use environment mapping).

        Raises:
            ArkException: In case of error, or tenant username prefix was not found in identity environment

        Returns:
            str: result of the identity request to get the tenant FQDN
        """
        identity_env_url = identity_env_url or (
            IDENTITY_ENV_URLS[AwsEnv(os.getenv('DEPLOY_ENV', None))] if os.getenv('DEPLOY_ENV', None) else IDENTITY_ENV_URLS[AwsEnv.PROD]
        )
        session = Session()
        response = session.post(
            f'https://pod0.{identity_env_url}/Security/StartAuthentication',
            json={'User': tenant_suffix, 'Version': '1.0', 'PlatformTokenResponse': True, 'MfaRequestor': 'DeviceAgent'},
            headers={'Content-Type': 'application/json', 'X-IDAP-NATIVE-CLIENT': 'true'},
        )
        try:
            parsed_res: TenantFqdnResponse = TenantFqdnResponse.parse_raw(response.text)
        except (ValidationError, TypeError) as ex:
            raise ArkException('Getting tenant FQDN failed to be parsed / validated') from ex
        if not parsed_res.result.pod_fqdn.startswith('https://'):
            parsed_res.result.pod_fqdn = f'https://{parsed_res.result.pod_fqdn}'
        return parsed_res.result.pod_fqdn
