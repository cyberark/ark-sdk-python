from typing import Dict, Final, Optional, Type

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.actions.ark_service_action_definition import ArkServiceActionDefinition
from ark_sdk_python.models.services.identity.connectors import ArkIdentityConnectorsFilter, ArkIdentityGetConnector
from ark_sdk_python.models.services.identity.directories import ArkIdentityListDirectories, ArkIdentityListDirectoriesEntities
from ark_sdk_python.models.services.identity.policies import (
    ArkIdentityAddAuthenticationProfile,
    ArkIdentityAddPolicy,
    ArkIdentityDisablePolicy,
    ArkIdentityEnablePolicy,
    ArkIdentityGetAuthenticationProfile,
    ArkIdentityGetPolicy,
    ArkIdentityRemoveAuthenticationProfile,
    ArkIdentityRemovePolicy,
)
from ark_sdk_python.models.services.identity.roles import (
    ArkIdentityAddAdminRightsToRole,
    ArkIdentityAddGroupToRole,
    ArkIdentityAddRoleToRole,
    ArkIdentityAddUserToRole,
    ArkIdentityCreateRole,
    ArkIdentityDeleteRole,
    ArkIdentityListRoleMembers,
    ArkIdentityRemoveGroupFromRole,
    ArkIdentityRemoveRoleFromRole,
    ArkIdentityRemoveUserFromRole,
    ArkIdentityRoleIdByName,
    ArkIdentityUpdateRole,
)
from ark_sdk_python.models.services.identity.users import (
    ArkIdentityCreateUser,
    ArkIdentityDeleteUser,
    ArkIdentityDeleteUsers,
    ArkIdentityResetUserPassword,
    ArkIdentityUpdateUser,
    ArkIdentityUserById,
    ArkIdentityUserByName,
    ArkIdentityUserIdByName,
)

# Identity Definitions
# Connectors
IDENTITY_CONNECTORS_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'list-connectors': None,
    'list-connectors-by': ArkIdentityConnectorsFilter,
    'connector': ArkIdentityGetConnector,
}
IDENTITY_CONNECTORS_ACTIONS: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='connectors',
    schemas=IDENTITY_CONNECTORS_ACTION_TO_SCHEMA_MAP,
)

# Directories
IDENTITY_DIRECTORIES_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'list-directories': ArkIdentityListDirectories,
    'list-directories-entities': ArkIdentityListDirectoriesEntities,
    'tenant-default-suffix': None,
}
IDENTITY_DIRECTORIES_ACTIONS: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='directories',
    schemas=IDENTITY_DIRECTORIES_ACTION_TO_SCHEMA_MAP,
)

# Policies
IDENTITY_POLICIES_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'add-authentication-profile': ArkIdentityAddAuthenticationProfile,
    'remove-authentication-profile': ArkIdentityRemoveAuthenticationProfile,
    'list-authentication-profiles': None,
    'authentication-profile': ArkIdentityGetAuthenticationProfile,
    'add-policy': ArkIdentityAddPolicy,
    'remove-policy': ArkIdentityRemovePolicy,
    'list-policies': None,
    'policy': ArkIdentityGetPolicy,
    'enable-policy': ArkIdentityEnablePolicy,
    'disable-policy': ArkIdentityDisablePolicy,
    'enable-default-policy': None,
    'disable-default-policy': None,
}
IDENTITY_POLICIES_ACTIONS: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='policies',
    schemas=IDENTITY_POLICIES_ACTION_TO_SCHEMA_MAP,
)

# Roles
IDENTITY_ROLES_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'add-user-to-role': ArkIdentityAddUserToRole,
    'add-group-to-role': ArkIdentityAddGroupToRole,
    'add-role-to-role': ArkIdentityAddRoleToRole,
    'remove-user-from-role': ArkIdentityRemoveUserFromRole,
    'remove-group-from-role': ArkIdentityRemoveGroupFromRole,
    'remove-role-from-role': ArkIdentityRemoveRoleFromRole,
    'create-role': ArkIdentityCreateRole,
    'update-role': ArkIdentityUpdateRole,
    'delete-role': ArkIdentityDeleteRole,
    'list-role-members': ArkIdentityListRoleMembers,
    'add-admin-rights-to-role': ArkIdentityAddAdminRightsToRole,
    'role-id-by-name': ArkIdentityRoleIdByName,
}
IDENTITY_ROLES_ACTIONS: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='roles',
    schemas=IDENTITY_ROLES_ACTION_TO_SCHEMA_MAP,
)

# Users
IDENTITY_USERS_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'create-user': ArkIdentityCreateUser,
    'update-user': ArkIdentityUpdateUser,
    'delete-user': ArkIdentityDeleteUser,
    'delete-users': ArkIdentityDeleteUsers,
    'user-by-id': ArkIdentityUserById,
    'user-by-name': ArkIdentityUserByName,
    'user-id-by-name': ArkIdentityUserIdByName,
    'reset-user-password': ArkIdentityResetUserPassword,
}
IDENTITY_USERS_ACTIONS: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='users',
    schemas=IDENTITY_USERS_ACTION_TO_SCHEMA_MAP,
)

# Service Actions Definition
IDENTITY_ACTIONS: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='identity',
    subactions=[
        IDENTITY_CONNECTORS_ACTIONS,
        IDENTITY_DIRECTORIES_ACTIONS,
        IDENTITY_POLICIES_ACTIONS,
        IDENTITY_ROLES_ACTIONS,
        IDENTITY_USERS_ACTIONS,
    ],
)
