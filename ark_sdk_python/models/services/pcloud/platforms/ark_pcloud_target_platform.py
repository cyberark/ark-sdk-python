from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkTitleizedModel


class ArkPCloudTPPrivilegedAccessWorkflowsActiveException(ArkTitleizedModel):
    is_active: Optional[bool] = Field(default=None, description='Whether workflow is active')
    is_an_exception: Optional[bool] = Field(default=None, description='Whether workflow is an exception')


class ArkPCloudTPPrivilegedAccessWorkflows(ArkTitleizedModel):
    require_dual_control_password_access_approval: Optional[ArkPCloudTPPrivilegedAccessWorkflowsActiveException] = Field(
        default=None, description='Dual control workflow details'
    )
    enforce_checkin_checkout_exclusive_access: Optional[ArkPCloudTPPrivilegedAccessWorkflowsActiveException] = Field(
        default=None, description='Checkin checkout workflow details'
    )
    enforce_onetime_password_access: Optional[ArkPCloudTPPrivilegedAccessWorkflowsActiveException] = Field(
        default=None, description='One time password workflow details'
    )
    require_users_to_specify_reason_for_access: Optional[ArkPCloudTPPrivilegedAccessWorkflowsActiveException] = Field(
        default=None, description='Specify reason workflow details'
    )


class ArkPCloudTPCredentialsManagementVerificationChangePolicy(ArkTitleizedModel):
    perform_automatic: Optional[bool] = Field(
        default=None, description='Indicates whether accounts related to this platform will be changed automatically'
    )
    require_password_every_x_days: Optional[int] = Field(default=None, description='The number of days between each periodic change')
    auto_on_add: Optional[bool] = Field(
        default=None, description='Indicates whether accounts related to this platform will be changed after being added'
    )
    is_require_password_every_x_days_an_exception: Optional[bool] = Field(
        default=None, description='Indicates whether the number of days between each periodic change is an exception to the master policy'
    )
    allow_manual: Optional[bool] = Field(
        default=None, description='Indicates whether an immediate change process can be initiated manually'
    )


class ArkPCloudTPCredentialsManagementReconcilePolicy(ArkTitleizedModel):
    automatic_reconcile_when_unsynced: Optional[bool] = Field(
        default=None,
        description='Indicates whether or not passwords will be reconciled automatically after the CPM detects a password on a remote machine that is not synchronized with its corresponding password in the Server',
    )
    allow_manual: Optional[bool] = Field(
        default=None, description='Indicates whether an immediate reconcile process can be initiated manually.'
    )


class ArkPCloudTPCredentialsManagementSecretUpdateConfiguration(ArkTitleizedModel):
    change_password_in_reset_mode: Optional[bool] = Field(
        default=None,
        description='Defines whether or not password changes will be performed via reset mode using the reconciliation account. This is useful in cases where the password policy prevents the user from changing his own password or when a password minimal age restriction is applied',
    )


class ArkPCloudTPCredentialsManagementPolicy(ArkTitleizedModel):
    verification: Optional[ArkPCloudTPCredentialsManagementVerificationChangePolicy] = Field(
        default=None, description='Verification policy'
    )
    change: Optional[ArkPCloudTPCredentialsManagementVerificationChangePolicy] = Field(default=None, description='Change policy')
    reconcile: Optional[ArkPCloudTPCredentialsManagementReconcilePolicy] = Field(default=None, description='Reconcile policy')
    secret_update_configuration: Optional[ArkPCloudTPCredentialsManagementSecretUpdateConfiguration] = Field(
        default=None, description='Secret update configuration'
    )


class ArkPCloudTPPrivilegedSessionManagement(ArkTitleizedModel):
    psm_server_id: Optional[str] = Field(default=None, description='PSM server id', alias='PSMServerId')
    psm_server_name: Optional[str] = Field(default=None, description='PSM server name', alias='PSMServerName')


class ArkPCloudTargetPlatform(ArkTitleizedModel):
    id: int = Field(description='Unique numeric ID of the platform', alias='ID')
    platform_id: str = Field(description='Unique string ID of the platform', alias='PlatformID')
    name: Optional[str] = Field(default=None, description='The display name of the platform')
    active: Optional[bool] = Field(default=None, description='Indicates whether a platform is active or inactive')
    system_type: Optional[str] = Field(default=None, description='The type of system associated with the target')
    allowed_safes: Optional[str] = Field(default=None, description='Regex of safes in which accounts from this platform can be managed')
    privileged_access_workflows: Optional[ArkPCloudTPPrivilegedAccessWorkflows] = Field(default=None, description='Workflows configuration')
    credentials_management_policy: Optional[ArkPCloudTPCredentialsManagementPolicy] = Field(default=None, description='CPM Policy')
    privileged_session_management: Optional[ArkPCloudTPPrivilegedSessionManagement] = Field(default=None, description='PSM Management')
