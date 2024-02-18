from typing import Dict, Final, List

CONFIGURATION_IGNORED_DEFINITION_KEYS: Final[List[str]] = [
    'auth-profiles',
    'auth-method',
    'auth-method-settings',
    'user-param-name',
    'password-param-name',
    'identity-mfa-interactive',
]
CONFIGURATION_AUTHENTICATOR_IGNORED_DEFNITION_KEYS: Final[Dict[str, List[str]]] = {
    'isp': ['identity-application', 'identity-tenant-url'],
}
CONFIGURATION_IGNORED_INTERACTIVE_KEYS: Final[List[str]] = [
    'raw',
    'silent',
    'verbose',
    'profile_name',
    'auth_profiles',
    'auth_method',
    'auth_method_settings',
    'interactive',
]
CONFIGURATION_AUTHENTICATOR_IGNORED_INTERACTIVE_KEYS: Final[Dict[str, List[str]]] = {
    'isp': [
        'identity_application',
        'identity_application_id',
        'identity_authorization_application',
        'identity_tenant_url',
    ],
}
CONFIGURATION_ALLOWED_EMPTY_VALUES: Final[List[str]] = {
    'isp_identity_url',
    'isp_identity_tenant_subdomain',
}
CONFIGURATION_AUTHENTICATORS_DEFAULTS: Final[Dict[str, str]] = {}
CONFIGURATION_OVERRIDE_ALIASES: Final[Dict[str, str]] = {'region': 'Region', 'env': 'Environment'}
