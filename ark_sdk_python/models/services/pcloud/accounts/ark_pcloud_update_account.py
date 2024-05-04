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
    name: Optional[str] = Field(description='Name of the account to update')
    address: Optional[str] = Field(description='Address of the account to update')
    username: Optional[str] = Field(description='Username of the account to update')
    platform_id: Optional[str] = Field(description='Platform id to relate the account to to update')
    safe_name: Optional[str] = Field(description='Safe name to store the account in to update')
    secret_type: Optional[ArkPCloudAccountSecretType] = Field(description='Type of the secret of the account to update')
    platform_account_properties: Optional[Dict[str, Any]] = Field(
        description='Different properties related to the platform the account is related to to update'
    )
    secret_management: Optional[ArkPCloudAccountSecretManagement] = Field(description='Secret mgmt related properties to update')
    remote_machines_access: Optional[ArkPCloudAccountRemoteMachinesAccess] = Field(
        description='Remote machines access related properties to update'
    )
