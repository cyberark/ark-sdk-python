from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityFederationGroupMapping(ArkModel):
    attribute_value: str = Field(description='The group value the identity provider asserts')
    group_name: str = Field(description='The federated group the asserted value maps to')


class ArkIdentityFederationAttributeMapping(ArkModel):
    target: str = Field(description='The Cloud Directory user attribute to set')
    source: str = Field(description='The identity provider attribute to read')


class ArkIdentityFederation(ArkModel):
    federation_id: str = Field(description='The unique identifier of the federation')
    federation_name: str = Field(description='The display name of the external identity provider')
    federation_type: str = Field(description='The federation protocol, SAML 2.0 or OIDC')
    active: bool = Field(description='Whether the federation is active', default=True)
    domains: List[str] = Field(description='The federated domains routed to this identity provider', default_factory=list)
    # OIDC
    oidc_metadata_url: Optional[str] = Field(description='The OIDC discovery document URL', default=None)
    oidc_client_id: Optional[str] = Field(description='The client ID registered at the OIDC identity provider', default=None)
    oidc_grant_type: Optional[str] = Field(description='The OIDC grant type', default=None)
    oidc_pkce_enabled: bool = Field(description='Whether PKCE is used', default=False)
    oidc_scopes: List[str] = Field(description='The scopes requested from the OIDC identity provider', default_factory=list)
    oidc_post_logout_redirect_uri: Optional[str] = Field(description='The post logout redirect URI', default=None)
    # SAML
    saml_metadata_url: Optional[str] = Field(description='The SAML identity provider metadata URL', default=None)
    saml_sign_in_url: Optional[str] = Field(description='The SAML identity provider sign in URL', default=None)
    saml_logout_url: Optional[str] = Field(description='The SAML identity provider logout URL', default=None)
    saml_sign_algorithm: Optional[str] = Field(description='The algorithm the SAML authentication request is signed with', default=None)
    saml_url_redirect_enabled: bool = Field(
        description='Whether users are redirected to a URL pattern after the SAML sign in', default=False
    )
    saml_url_redirect_pattern: Optional[str] = Field(
        description='The URL pattern redirection after the SAML sign in is allowed to', default=None
    )
    saml_oauth_client_id: Optional[str] = Field(description='The OAuth client id used for the password sign in', default=None)
    saml_oauth_access_token_url: Optional[str] = Field(description='The OAuth token url of the identity provider', default=None)
    saml_idp_certificate_thumbprint: Optional[str] = Field(description='Thumbprint of the SAML signing certificate', default=None)
    saml_idp_certificate_subject: Optional[str] = Field(description='Subject of the SAML signing certificate', default=None)
    saml_idp_certificate_expires: Optional[str] = Field(description='Expiry of the SAML signing certificate', default=None)
    saml_sp_metadata_url: Optional[str] = Field(description='The service provider metadata URL', default=None)
    # Mapping and routing
    map_users: str = Field(
        description='Whether federated users are linked to existing directory users, Disabled, Optional or Required', default='Disabled'
    )
    map_user_attribute: str = Field(
        description='The identity provider attribute used to find the directory user', default='UserPrincipalName'
    )
    map_user_directory_service: Optional[str] = Field(
        description='The directory service UUID searched for the user, empty means any', default=None
    )
    map_user_by: str = Field(description='The directory user attribute matched against map_user_attribute', default='Name')
    map_user_sync_with_cloud_user: bool = Field(
        description='Whether the directory user is updated from the identity provider', default=False
    )
    map_user_sync_with_federated_user: bool = Field(
        description='Whether the federated user is updated from the identity provider', default=True
    )
    map_user_uses_groups: bool = Field(description='Whether the mapped user also receives the federated group memberships', default=False)
    map_user_allow_other_federations: bool = Field(description='Whether the user may map to a user of another federation', default=False)
    map_user_create_if_not_found: bool = Field(description='Whether a Cloud Directory user is created when none is found', default=False)
    group_mappings: List[ArkIdentityFederationGroupMapping] = Field(
        description='Group assertions mapped to federated groups', default_factory=list
    )
    attribute_mappings: List[ArkIdentityFederationAttributeMapping] = Field(
        description='Identity provider attributes copied onto user attributes', default_factory=list
    )
    device_types: List[str] = Field(description='The device types routed to this identity provider, empty means all', default_factory=list)
    user_agents: List[str] = Field(description='The client types routed to this identity provider', default_factory=list)
