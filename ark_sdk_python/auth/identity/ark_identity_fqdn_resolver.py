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
        Resolves the tenant's FQDN URL from its subdomain.
        The resolved URL is based on the current working environment, which is provided in the `tenant_subdomain` argument.

        Args:
            tenant_subdomain (str): The tenant subdomain, for example: `mytenant`
            env (AwsEnv): The environment for which the the tenant URL is resolved

        Raises:
            ArkException: When an error occurs or the tenant username prefix was not found in the Identity environment

        Returns:
            str: The tenant's resolved FQDN
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
                parsed_response: IdentityEndpointResponse = IdentityEndpointResponse.model_validate_json(response.text)
                return str(parsed_response.endpoint)
        except (ValidationError, TypeError) as ex:
            raise ArkException('Getting tenant FQDN failed from platform discovery to be parsed / validated') from ex
        raise ArkException(f'Getting tenant FQDN failed from platform discovery [{response.status_code}] - [{response.text}]')

    @staticmethod
    @cached(cache=LRUCache(maxsize=1024))
    def resolve_tenant_fqdn_from_tenant_suffix(tenant_suffix: str, identity_env_url: Optional[str] = None) -> str:
        """
        Resolves the tenant's FQDN URL in Identity.
        By default, the Identity address is resolved from the current environment mapping (see `get_identity_env_url()`), but it can be optionally be resolved from the `identity_env_url` argument.

        Args:
            tenant_suffix (str): The tenant's URL suffix, for example: `@tenant-a-527.shell.cyberark.cloud`
            identity_env_url (str, optional): If specified, used as the Identity pod0 URL; otherwise, defaults to `None` (use environment mapping)

        Raises:
            ArkException: In case of error, or tenant username prefix was not found in identity environment

        Returns:
            str: The tenant's FQDN
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
            parsed_res: TenantFqdnResponse = TenantFqdnResponse.model_validate_json(response.text)
        except (ValidationError, TypeError) as ex:
            raise ArkException('Getting tenant FQDN failed to be parsed / validated') from ex
        if not parsed_res.result.pod_fqdn.startswith('https://'):
            parsed_res.result.pod_fqdn = f'https://{parsed_res.result.pod_fqdn}'
        return parsed_res.result.pod_fqdn
