from typing import Any, Dict, Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.pcloud.accounts.ark_pcloud_account import (
    ArkPCloudAccountRemoteMachinesAccess,
    ArkPCloudAccountSecretManagement,
    ArkPCloudAccountSecretType,
)


class ArkPCloudUpdateAccount(ArkCamelizedModel):
    account_id: str = Field(description='The account id to update')
    name: Optional[str] = Field(default=None, description='Name of the account to update')
    address: Optional[str] = Field(default=None, description='Address of the account to update')
    username: Optional[str] = Field(default=None, description='Username of the account to update')
    platform_id: Optional[str] = Field(default=None, description='Platform id to relate the account to to update')
    safe_name: Optional[str] = Field(default=None, description='Safe name to store the account in to update')
    secret_type: Optional[ArkPCloudAccountSecretType] = Field(default=None, description='Type of the secret of the account to update')
    platform_account_properties: Optional[Dict[str, Any]] = Field(
        default=None, description='Different properties related to the platform the account is related to to update'
    )
    secret_management: Optional[ArkPCloudAccountSecretManagement] = Field(
        default=None, description='Secret mgmt related properties to update'
    )
    remote_machines_access: Optional[ArkPCloudAccountRemoteMachinesAccess] = Field(
        default=None, description='Remote machines access related properties to update'
    )
