from enum import Enum
from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkPCloudPlatformType(str, Enum):
    Regular = 'regular'
    Group = 'group'
    RotationalGroups = 'rotationalgroup'
    Dependent = 'dependent'


class ArkPCloudPlatformGeneralDetails(ArkCamelizedModel):
    id: str = Field(description='ID of the platform')
    name: str = Field(description='Name of the platform')
    system_type: str = Field(description='System type of the platform')
    active: bool = Field(description='Whether this platform is active or not')
    description: str = Field(description='Description about the platform')
    platform_base_id: Optional[str] = Field(description='Base ID of the platform if inherits from another one', default=None)
    platform_type: ArkPCloudPlatformType = Field(description='Type of the platform')


class ArkPCloudPlatformProperty(ArkCamelizedModel):
    name: Optional[str] = Field(description='Property name', default=None)
    display_name: Optional[str] = Field(description='Property display name', default=None)


class ArkPCloudPlatformProperties(ArkCamelizedModel):
    required: List[ArkPCloudPlatformProperty] = Field(description='Required platform properties')
    optional: List[ArkPCloudPlatformProperty] = Field(description='Optional platform properties')


class ArkPCloudCredentialsManagement(ArkCamelizedModel):
    allowed_safes: str = Field(description='Which safes regex are allowed for credentials management')
    allow_manual_change: bool = Field(description='Whether manual change of credentials is allowed')
    perform_periodic_change: bool = Field(description='Whether to perform periodic change of credentials')
    require_password_change_every_x_days: int = Field(description='Every how much time to perfrom the periodic change')
    allow_manual_verification: bool = Field(description='Allow manual verification of credentials')
    perform_periodic_verification: bool = Field(description='Whether to perform periodic verification of credentials')
    require_password_verification_every_x_days: int = Field(description='Every how much time to perform periodic verification')
    allow_manual_reconciliation: bool = Field(description='Allow manual reconciliation of credentials')
    automatic_reconcile_when_unsynched: bool = Field(description='Reconcile credentials automatically when unsynced')


class ArkPCloudSessionManagement(ArkCamelizedModel):
    require_privileged_session_monitoring_and_isolation: bool = Field(description='Whether sessions require PSM isolation and monitoring')
    record_and_save_session_activity: bool = Field(description='Whether to record and save session activity')
    psm_server_id: Optional[str] = Field(description='ID of the psm server installed', default=None)


class ArkPCloudPrivilegedAccessWorkflows(ArkCamelizedModel):
    require_dual_control_password_access_approval: bool = Field(description='Whether dual control is required for access')
    enforce_checkin_checkout_exclusive_access: bool = Field(description='Whether to enforce exclusive access')
    enforce_onetime_password_access: bool = Field(description='Whether to enforce one time password access')


class ArkPCloudPlatform(ArkCamelizedModel):
    general: ArkPCloudPlatformGeneralDetails = Field(description='General platform settings')
    properties: ArkPCloudPlatformProperties = Field(description='Platform properties')
    linked_accounts: List[ArkPCloudPlatformProperty] = Field(description='Platform linked accounts')
    credentials_management: ArkPCloudCredentialsManagement = Field(description='Platform credentials management properties')
    session_management: ArkPCloudSessionManagement = Field(description='Platform session management properties')
    privileged_access_workflows: ArkPCloudPrivilegedAccessWorkflows = Field(description='Platform privileged access workflows properties')
