from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import Field, field_validator

from ark_sdk_python.models import ArkCamelizedModel


class ArkPCloudAccountSecretType(str, Enum):
    Password = "password"
    Key = "key"


class ArkPCloudAccountSecretManagement(ArkCamelizedModel):
    automatic_management_enabled: Optional[bool] = Field(
        default=None, description='Whether automatic management of the account is enabled or not'
    )
    manual_management_reason: Optional[str] = Field(default=None, description='The reason for disabling automatic management')
    last_modified_time: Optional[int] = Field(default=None, description='Last time the management properties were modified')


class ArkPCloudAccountRemoteMachinesAccess(ArkCamelizedModel):
    remote_machines: Optional[Union[List[str], str]] = Field(
        default=None, description='Remote machines the access of this account is allowed'
    )
    access_restricted_to_remote_machines: Optional[bool] = Field(
        default=None, description='Whether the access is only restricted to those remote machines'
    )

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('remote_machines', mode="before")
    @classmethod
    def _validate_remote_machines(cls, remote_machines):
        # backward compatibility for when remote_machines was a comma separated string
        if isinstance(remote_machines, str):
            return remote_machines.split(',')
        return remote_machines


class ArkPCloudBaseAccount(ArkCamelizedModel):
    name: str = Field(description='Name of the account')
    safe_name: str = Field(description='Safe name to store the account in')
    platform_id: Optional[str] = Field(default=None, description='Platform id to relate the account to')
    user_name: Optional[str] = Field(default=None, description='Username of the account')
    address: Optional[str] = Field(default=None, description='Address of the account')
    secret_type: Optional[ArkPCloudAccountSecretType] = Field(default=None, description='Type of the secret of the account')
    platform_account_properties: Optional[Dict[str, Any]] = Field(
        default=None, description='Different properties related to the platform the account is related to'
    )
    secret_management: Optional[ArkPCloudAccountSecretManagement] = Field(default=None, description='Secret mgmt related properties')
    remote_machines_access: Optional[ArkPCloudAccountRemoteMachinesAccess] = Field(
        default=None, description='Remote machines access related properties'
    )


class ArkPCloudAccount(ArkPCloudBaseAccount):
    id: str = Field(description='ID of the account')
    status: Optional[str] = Field(default=None, description='Status of the account')
    created_time: Optional[int] = Field(default=None, description='Creation time of the account')
    category_modification_time: Optional[int] = Field(default=None, description='Category modification time of the account')
