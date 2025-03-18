from typing import Dict, Final, Optional, Type

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.actions.ark_service_action_definition import ArkServiceActionDefinition
from ark_sdk_python.models.services.pcloud.accounts import (
    ArkPCloudAccountsFilter,
    ArkPCloudAddAccount,
    ArkPCloudChangeAccountCredentials,
    ArkPCloudDeleteAccount,
    ArkPCloudGenerateAccountCredentials,
    ArkPCloudGetAccount,
    ArkPCloudGetAccountCredentials,
    ArkPCloudLinkAccount,
    ArkPCloudListAccountSecretVersions,
    ArkPCloudReconcileAccountCredentials,
    ArkPCloudSetAccountNextCredentials,
    ArkPCloudUnlinkAccount,
    ArkPCloudUpdateAccount,
    ArkPCloudUpdateAccountCredentialsInVault,
    ArkPCloudVerifyAccountCredentials,
)
from ark_sdk_python.models.services.pcloud.applications import (
    ArkPCloudAddApplication,
    ArkPCloudAddApplicationAuthMethod,
    ArkPCloudApplicationAuthMethodsFilter,
    ArkPCloudApplicationsFilter,
    ArkPCloudDeleteApplication,
    ArkPCloudDeleteApplicationAuthMethod,
    ArkPCloudGetApplication,
    ArkPCloudGetApplicationAuthMethod,
    ArkPCloudListApplicationAuthMethods,
)
from ark_sdk_python.models.services.pcloud.platforms import (
    ArkPCloudActivateTargetPlatform,
    ArkPCloudDeactivateTargetPlatform,
    ArkPCloudDeleteTargetPlatform,
    ArkPCloudDuplicateTargetPlatform,
    ArkPCloudExportPlatform,
    ArkPCloudExportTargetPlatform,
    ArkPCloudGetPlatform,
    ArkPCloudGetTargetPlatform,
    ArkPCloudImportPlatform,
    ArkPCloudImportTargetPlatform,
    ArkPCloudPlatformsFilter,
    ArkPCloudTargetPlatformsFilter,
)
from ark_sdk_python.models.services.pcloud.safes import (
    ArkPCloudAddSafe,
    ArkPCloudAddSafeMember,
    ArkPCloudDeleteSafe,
    ArkPCloudDeleteSafeMember,
    ArkPCloudGetSafe,
    ArkPCloudGetSafeMember,
    ArkPCloudGetSafeMembersStats,
    ArkPCloudListSafeMembers,
    ArkPCloudSafeMembersFilters,
    ArkPCloudSafesFilters,
    ArkPCloudUpdateSafe,
    ArkPCloudUpdateSafeMember,
)

# PCloud Accounts Definitions
PCLOUD_ACCOUNTS_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'add-account': ArkPCloudAddAccount,
    'update-account': ArkPCloudUpdateAccount,
    'delete-account': ArkPCloudDeleteAccount,
    'account': ArkPCloudGetAccount,
    'account-credentials': ArkPCloudGetAccountCredentials,
    'list-accounts': None,
    'list-accounts-by': ArkPCloudAccountsFilter,
    'list-account-secret-versions': ArkPCloudListAccountSecretVersions,
    'generate-account-credentials': ArkPCloudGenerateAccountCredentials,
    'verify-account-credentials': ArkPCloudVerifyAccountCredentials,
    'change-account-credentials': ArkPCloudChangeAccountCredentials,
    'set-account-next-credentials': ArkPCloudSetAccountNextCredentials,
    'update-account-credentials-in-vault': ArkPCloudUpdateAccountCredentialsInVault,
    'reconcile-account-credentials': ArkPCloudReconcileAccountCredentials,
    'accounts-stats': None,
    'link-account': ArkPCloudLinkAccount,
    'unlink-account': ArkPCloudUnlinkAccount,
}
PCLOUD_ACCOUNTS_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='accounts',
    schemas=PCLOUD_ACCOUNTS_ACTION_TO_SCHEMA_MAP,
)

# PCloud Safes Definitions
PCLOUD_SAFES_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'add-safe': ArkPCloudAddSafe,
    'update-safe': ArkPCloudUpdateSafe,
    'delete-safe': ArkPCloudDeleteSafe,
    'safe': ArkPCloudGetSafe,
    'list-safes': None,
    'list-safes-by': ArkPCloudSafesFilters,
    'safes-stats': None,
    'add-safe-member': ArkPCloudAddSafeMember,
    'update-safe-member': ArkPCloudUpdateSafeMember,
    'delete-safe-member': ArkPCloudDeleteSafeMember,
    'safe-member': ArkPCloudGetSafeMember,
    'list-safe-members': ArkPCloudListSafeMembers,
    'list-safe-members-by': ArkPCloudSafeMembersFilters,
    'safe-members-stats': ArkPCloudGetSafeMembersStats,
    'safes-members-stats': None,
}
PCLOUD_SAFES_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='safes',
    schemas=PCLOUD_SAFES_ACTION_TO_SCHEMA_MAP,
)

# PCloud Platforms Definitions
PCLOUD_PLATFORMS_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'list-platforms': None,
    'list-platforms-by': ArkPCloudPlatformsFilter,
    'import-platform': ArkPCloudImportPlatform,
    'import-target-platform': ArkPCloudImportTargetPlatform,
    'export-platform': ArkPCloudExportPlatform,
    'export-target-platform': ArkPCloudExportTargetPlatform,
    'platform': ArkPCloudGetPlatform,
    'platforms-stats': None,
    'activate-target-platform': ArkPCloudActivateTargetPlatform,
    'deactivate-target-platform': ArkPCloudDeactivateTargetPlatform,
    'list-target-platforms': None,
    'list-target-platforms-by': ArkPCloudTargetPlatformsFilter,
    'target-platform': ArkPCloudGetTargetPlatform,
    'delete-target-platform': ArkPCloudDeleteTargetPlatform,
    'duplicate-target-platform': ArkPCloudDuplicateTargetPlatform,
    'target-platforms-stats': None,
}
PCLOUD_PLATFORMS_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='platforms',
    schemas=PCLOUD_PLATFORMS_ACTION_TO_SCHEMA_MAP,
)

# PCloud Applications Definitions
PCLOUD_APPLICATIONS_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'add-application': ArkPCloudAddApplication,
    'delete-application': ArkPCloudDeleteApplication,
    'list-applications': None,
    'list-applications-by': ArkPCloudApplicationsFilter,
    'application': ArkPCloudGetApplication,
    'applications-stats': None,
    'add-application-auth-method': ArkPCloudAddApplicationAuthMethod,
    'delete-application-auth-method': ArkPCloudDeleteApplicationAuthMethod,
    'list-application-auth-methods': ArkPCloudListApplicationAuthMethods,
    'list-application-auth-methods-by': ArkPCloudApplicationAuthMethodsFilter,
    'application-auth-method': ArkPCloudGetApplicationAuthMethod,
}
PCLOUD_APPLICATIONS_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='applications',
    schemas=PCLOUD_APPLICATIONS_ACTION_TO_SCHEMA_MAP,
)

# Service Actions Definition
PCLOUD_ACTIONS: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='pcloud',
    subactions=[
        PCLOUD_ACCOUNTS_ACTION,
        PCLOUD_PLATFORMS_ACTION,
        PCLOUD_SAFES_ACTION,
        PCLOUD_APPLICATIONS_ACTION,
    ],
)
