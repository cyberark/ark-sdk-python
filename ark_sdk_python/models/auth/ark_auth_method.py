from enum import Enum
from typing import Dict, List, Optional, Type, Union

from pydantic import Field
from typing_extensions import Literal

from ark_sdk_python.models.ark_model import ArkModel


class ArkAuthMethod(str, Enum):
    Identity = 'identity'
    IdentityServiceUser = 'identity_service_user'
    Direct = 'direct'
    Default = 'default'
    Other = 'other'


class ArkAuthMethodSettings(ArkModel):
    pass


class IdentityArkAuthMethodSettings(ArkAuthMethodSettings):
    identity_mfa_method: Literal['pf', 'sms', 'email', 'otp', 'oath', ''] = Field(
        description='MFA method if mfa is needed', default='email', alias='MFA Method to use by default [pf, sms, email, otp]'
    )
    identity_mfa_interactive: bool = Field(description='Allow interactive MFA (passcodes)', alias='Allow Interactive MFA', default=True)
    identity_application: Optional[str] = Field(
        default=None, description='Identity application to use once logged in', alias='Identity Application'
    )
    identity_url: Optional[str] = Field(
        default=None, description='Identity url to use for authentication instead of fqdn resolving', alias='Identity Url'
    )
    identity_tenant_subdomain: Optional[str] = Field(
        default=None,
        description='Identity security platform tenant subdomain, '
        'for exmaple mytenant.cyberark.cloud would be subdomained to mytenant. '
        'this will be used instead of fqdn resolving from the username',
        alias='Identity Tenant Subdomain',
    )


class IdentityServiceUserArkAuthMethodSettings(ArkAuthMethodSettings):
    identity_authorization_application: str = Field(
        description='Identity application to authorize once logged in with the service user',
        default='__idaptive_cybr_user_oidc',
        alias='Service User Authorization Application',
    )


class DirectArkAuthMethodSettings(ArkAuthMethodSettings):
    endpoint: Optional[str] = Field(description='Direct authentication endpoint', alias='Authentication Endpoint', default=None)
    interactive: bool = Field(description='Allow interactiveness', alias='Allow interactiveness', default=True)


class DefaultArkAuthMethodSettings(ArkAuthMethodSettings):
    pass


ArkAuthMethodSettingsTypes = Union[
    (IdentityArkAuthMethodSettings, IdentityServiceUserArkAuthMethodSettings, DirectArkAuthMethodSettings, DefaultArkAuthMethodSettings)
]
ArkAuthMethodSettingsMap: Dict[(ArkAuthMethod, Type[ArkAuthMethodSettings])] = {
    ArkAuthMethod.Identity: IdentityArkAuthMethodSettings,
    ArkAuthMethod.IdentityServiceUser: IdentityServiceUserArkAuthMethodSettings,
    ArkAuthMethod.Direct: DirectArkAuthMethodSettings,
    ArkAuthMethod.Default: DefaultArkAuthMethodSettings,
}
ArkAuthMethodsDescriptionMap: Dict[(ArkAuthMethod, str)] = {
    ArkAuthMethod.Identity: 'Identity Personal User',
    ArkAuthMethod.IdentityServiceUser: 'Identity Service User',
    ArkAuthMethod.Direct: 'Direct Endpoint Access',
    ArkAuthMethod.Default: 'Default Authenticator Method',
}
ArkAuthMethodsRequireCredentials: List[ArkAuthMethod] = [ArkAuthMethod.Identity, ArkAuthMethod.IdentityServiceUser, ArkAuthMethod.Direct]
ArkAuthMethodSharableCredentials: List[ArkAuthMethod] = [ArkAuthMethod.Identity]
