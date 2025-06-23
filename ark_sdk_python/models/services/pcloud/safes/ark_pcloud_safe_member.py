from enum import Enum
from typing import Optional, Union

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkPCloudSafeMemberType(str, Enum):
    User = "User"
    Group = "Group"
    Role = "Role"


class ArkPCloudSafeMemberPermissionSet(str, Enum):
    ConnectOnly = 'connect_only'  # Connect only permission set containing List and Use Accounts permissions
    ReadOnly = 'read_only'  # Read only permission set containing List, Use and Retrieve Accounts permissions
    Approver = 'approver'  # Approver permission set containing List accounts, View and Manage Safe members, and level 1 confirm / authorization level
    AccountsManager = 'accounts_manager'  # Accounts manager permission set containing Read, Write Accounts, View and Manage safe members and audit logs, and access safe without permissions
    Full = 'full'  # Full permissions
    Custom = 'custom'  # Custom permission set defined by the permissions object itself


class ArkPCloudSafeMemberPermissions(ArkCamelizedModel):
    use_accounts: bool = Field(description='Use accounts permission', default=False)
    retrieve_accounts: bool = Field(description='Retrieve accounts permission', default=False)
    list_accounts: bool = Field(description='List accounts permission', default=False)
    add_accounts: bool = Field(description='Add accounts permission', default=False)
    update_account_content: bool = Field(description='Update account content permission', default=False)
    update_account_properties: bool = Field(description='Update account properties permission', default=False)
    initiate_cpm_account_management_operations: bool = Field(
        description='Initate CPM account management operations permission', default=False, alias='initiateCPMAccountManagementOperations'
    )
    specify_next_account_content: bool = Field(description='Specify next account content permissions', default=False)
    rename_accounts: bool = Field(description='Rename accounts permission', default=False)
    delete_accounts: bool = Field(description='Delete accounts permission', default=False)
    unlock_accounts: bool = Field(description='Unlock accounts permission', default=False)
    manage_safe: bool = Field(description='Manage safe permission', default=False)
    manage_safe_members: bool = Field(description='Manage safe members', default=False)
    backup_safe: bool = Field(description='Backup safe permission', default=False)
    view_audit_log: bool = Field(description='View audit log permission', default=False)
    view_safe_members: bool = Field(description='View safe members permission', default=False)
    access_without_confirmation: bool = Field(description='Access without confirmation permission', default=False)
    create_folders: bool = Field(description='Create folders permission', default=False)
    delete_folders: bool = Field(description='Delete folders permission', default=False)
    move_accounts_and_folders: bool = Field(description='Move accounts and folders permission', default=False)
    requests_authorization_level1: bool = Field(description='Request authorization level 1 permission', default=False)
    requests_authorization_level2: bool = Field(description='Request authorization level 2 permission', default=False)


class ArkPCloudSafeMember(ArkCamelizedModel):
    safe_url_id: str = Field(description='Safe url identifier')
    safe_name: str = Field(description='Name of the safe of the member')
    safe_number: int = Field(description='Number id of the safe')
    member_id: Union[int, str] = Field(description='Member id')
    member_name: str = Field(description='Name of the member of the safe')
    member_type: ArkPCloudSafeMemberType = Field(description='Type of the member of the safe')
    membership_expiration_date: Optional[int] = Field(description='Expiration date of the member on the safe')
    is_expired_membership_enable: Optional[bool] = Field(description='Whether expired membership is enabled or not')
    is_predefined_user: bool = Field(description='Whether this is a predefined user or not')
    is_read_only: bool = Field(description='Whether this member is read only')
    permissions: ArkPCloudSafeMemberPermissions = Field(description='Permissions of the safe member')
    permission_set: ArkPCloudSafeMemberPermissionSet = Field(
        description='Permission set type the permissions are set to', default=ArkPCloudSafeMemberPermissionSet.Custom
    )
