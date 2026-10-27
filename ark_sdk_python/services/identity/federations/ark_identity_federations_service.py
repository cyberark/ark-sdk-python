from http import HTTPStatus
from typing import Any, Dict, Final, List, Optional

from overrides import overrides
from pydantic import ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.models.ark_exceptions import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.identity.federations import (
    ArkIdentityFederation,
    ArkIdentityFederationAttributeMapping,
    ArkIdentityFederationGroupMapping,
    ArkIdentityFederationsFilter,
    ArkIdentityGetFederation,
)
from ark_sdk_python.services.identity.common import ArkIdentityBaseService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='identity-federations', required_authenticator_names=['isp'], optional_authenticator_names=[]
)

LIST_FEDERATIONS_URL: Final[str] = 'Federation/GetFederations'
GET_FEDERATION_URL: Final[str] = 'Federation/GetFederation'

FEDERATION_TYPE_SAML: Final[str] = 'SAML 2.0'
FEDERATION_TYPE_OIDC: Final[str] = 'OIDC'
SUPPORTED_FEDERATION_TYPES: Final[List[str]] = [FEDERATION_TYPE_SAML, FEDERATION_TYPE_OIDC]

# The server applies these when a column is absent, so a read reports them as well
DEFAULT_MAP_USERS: Final[str] = 'Disabled'
DEFAULT_MAP_USER_ATTRIBUTE: Final[str] = 'UserPrincipalName'
DEFAULT_MAP_USER_BY: Final[str] = 'Name'
DEFAULT_SAML_SIGN_ALGORITHM: Final[str] = 'SHA1'
MAP_USERS_NAMES: Final[List[str]] = ['Disabled', 'Optional', 'Required']


def _string(raw: Optional[Dict[str, Any]], key: str) -> str:
    value = (raw or {}).get(key)
    return value if isinstance(value, str) else ''


def _bool(raw: Dict[str, Any], key: str, fallback: bool) -> bool:
    """A flag the server stores as a bool or, when it came from a form post, as the string true / false"""
    value = raw.get(key)
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().lower() in ('true', 'false'):
        return value.strip().lower() == 'true'
    return fallback


def _list(raw: Dict[str, Any], key: str) -> List[str]:
    """A list column, which can also come back as a comma separated string"""
    value = raw.get(key)
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item]
    if isinstance(value, str):
        return [item.strip() for item in value.split(',') if item.strip()]
    return []


def _map_users(raw: Dict[str, Any]) -> str:
    value = raw.get('MapUsers')
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return MAP_USERS_NAMES[int(value)] if 0 <= int(value) < len(MAP_USERS_NAMES) else DEFAULT_MAP_USERS
    if isinstance(value, str) and value:
        if value.isdigit():
            return MAP_USERS_NAMES[int(value)] if int(value) < len(MAP_USERS_NAMES) else DEFAULT_MAP_USERS
        return value
    return DEFAULT_MAP_USERS


def parse_federation(raw: Dict[str, Any]) -> ArkIdentityFederation:
    """Parses a federation as the Federation/GetFederations and Federation/GetFederation calls report it"""
    config = raw.get('Config') if isinstance(raw.get('Config'), dict) else {}
    federation_type = _string(raw, 'FederationType')
    federation = ArkIdentityFederation(
        federation_id=_string(raw, 'FederationUuid'),
        federation_name=_string(raw, 'FederationName'),
        federation_type=federation_type,
        active=_bool(raw, 'Active', True),
        domains=_list(raw, 'Domains'),
        map_users=_map_users(raw),
        map_user_attribute=_string(raw, 'MapUserAttribute') or DEFAULT_MAP_USER_ATTRIBUTE,
        map_user_by=_string(raw, 'MapUserBy') or DEFAULT_MAP_USER_BY,
        map_user_directory_service=_string(raw, 'MapUserDirectoryService') or None,
        map_user_sync_with_cloud_user=_bool(raw, 'MapUserSyncWithCloudUser', False),
        map_user_sync_with_federated_user=_bool(raw, 'MapUserSyncWithFedUser', True),
        map_user_uses_groups=_bool(raw, 'MapUserUsesGroups', False),
        map_user_allow_other_federations=_bool(raw, 'MapUserAllowFederations', False),
        map_user_create_if_not_found=_bool(raw, 'MapUserCreateIfNotFound', False),
        group_mappings=[
            ArkIdentityFederationGroupMapping(attribute_value=_string(item, 'AttributeValue'), group_name=_string(item, 'GroupName'))
            for item in raw.get('Mappings') or []
            if isinstance(item, dict)
        ],
        attribute_mappings=[
            ArkIdentityFederationAttributeMapping(target=_string(item, 'Target'), source=_string(item, 'Source'))
            for item in raw.get('AttributeMappings') or []
            if isinstance(item, dict)
        ],
        device_types=_list(raw, 'DeviceTypes'),
        user_agents=_list(raw, 'UserAgents') or ['Any'],  # the server stores Any when none is sent
    )
    if federation_type == FEDERATION_TYPE_SAML:
        federation.saml_metadata_url = _string(config, 'IDPMetadataUrl')
        federation.saml_sign_in_url = _string(config, 'IDPSignInUrl')
        federation.saml_logout_url = _string(config, 'IDPLogoutUrl')
        federation.saml_idp_certificate_thumbprint = _string(config, 'IDPSigningCertificateThumbprint')
        federation.saml_idp_certificate_subject = _string(config, 'IDPSigningCertificateSubject')
        federation.saml_idp_certificate_expires = _string(config, 'IDPSigningCertificateExpires')
        federation.saml_sign_algorithm = _string(raw, 'SAMLSignAlgorithm') or DEFAULT_SAML_SIGN_ALGORITHM
        federation.saml_url_redirect_enabled = _bool(raw, 'EnableUrlRedirecting', False)
        federation.saml_url_redirect_pattern = _string(raw, 'UrlPattern')
        federation.saml_oauth_client_id = _string(raw, 'OAuthClientId')
        federation.saml_oauth_access_token_url = _string(raw, 'OAuthAccessTokenUrl')
        federation.saml_sp_metadata_url = _string(raw, 'SPMetadataUrl')
    elif federation_type == FEDERATION_TYPE_OIDC:
        federation.oidc_metadata_url = _string(raw, 'OIDCMetaDataUrl')
        federation.oidc_client_id = _string(raw, 'OIDCClientId')
        federation.oidc_grant_type = _string(raw, 'OIDCGrantType')
        federation.oidc_pkce_enabled = _bool(raw, 'PKCEEnabled', False)
        federation.oidc_scopes = _list(raw, 'OIDCScopes')
        federation.oidc_post_logout_redirect_uri = _string(config, 'LogoutCallBackURI')
    return federation


class ArkIdentityFederationsService(ArkIdentityBaseService):
    """
    Read only access to the external identity providers (SAML 2.0 and OIDC federations) of the tenant.
    The OIDC client secret is never read, and the service provider urls (ACS, redirect) are not filled.
    """

    def __post(self, url: str, body: Dict[str, Any], action: str) -> Any:
        response: Response = self._client.post(f'{self._url_prefix}{url}', json=body)
        if response.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to {action} [{response.text}] - [{response.status_code}]')
        try:
            result = response.json()
            if not result['success']:
                raise ArkServiceException(f'Failed to {action} [{response.text}]')
            return result.get('Result')
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse {action} response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse {action} response [{str(ex)}]') from ex

    def __list_raw(self) -> List[Dict[str, Any]]:
        result = self.__post(LIST_FEDERATIONS_URL, {}, 'list identity federations')
        if not isinstance(result, list):
            raise ArkServiceException(f'Failed to parse identity federations [{result}]')
        return [row for row in result if isinstance(row, dict)]

    def list_federations(self) -> List[ArkIdentityFederation]:
        """
        Lists every SAML 2.0 and OIDC federation (external identity provider) of the tenant

        Raises:
            ArkServiceException: _description_

        Returns:
            List[ArkIdentityFederation]: _description_
        """
        self._logger.info('Listing identity federations')
        return [parse_federation(raw) for raw in self.__list_raw() if _string(raw, 'FederationType') in SUPPORTED_FEDERATION_TYPES]

    def list_federations_by(self, federations_filter: ArkIdentityFederationsFilter) -> List[ArkIdentityFederation]:
        """
        Lists the federations matching the given filters

        Args:
            federations_filter (ArkIdentityFederationsFilter): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            List[ArkIdentityFederation]: _description_
        """
        federations = self.list_federations()
        if federations_filter.federation_name:
            federations = [f for f in federations if f.federation_name.lower() == federations_filter.federation_name.lower()]
        if federations_filter.federation_type:
            federations = [f for f in federations if f.federation_type == federations_filter.federation_type]
        return federations

    def federation(self, get_federation: ArkIdentityGetFederation) -> ArkIdentityFederation:
        """
        Gets a federation by its id

        Args:
            get_federation (ArkIdentityGetFederation): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkIdentityFederation: _description_
        """
        self._logger.info(f'Retrieving identity federation [{get_federation.federation_id}]')
        try:
            result = self.__post(GET_FEDERATION_URL, {'FederationUuid': get_federation.federation_id}, 'retrieve identity federation')
        except ArkServiceException:
            # GetFederation reports a missing federation only through a localized message, so the listing decides
            if all(_string(raw, 'FederationUuid') != get_federation.federation_id for raw in self.__list_raw()):
                raise ArkServiceException(f'Identity federation [{get_federation.federation_id}] was not found') from None
            raise
        if not isinstance(result, dict):
            raise ArkServiceException(f'Failed to parse identity federation [{result}]')
        if _string(result, 'FederationType') not in SUPPORTED_FEDERATION_TYPES:
            raise ArkServiceException(f'Unsupported federation type [{_string(result, "FederationType")}]')
        return parse_federation(result)

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
