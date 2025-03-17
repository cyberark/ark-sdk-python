from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import Field, field_validator

from ark_sdk_python.models import ArkCamelizedModel


class ArkPCloudAccountSecretType(str, Enum):
    Password = "password"
    Key = "key"


class ArkPCloudAccountSecretManagement(ArkCamelizedModel):
    automatic_management_enabled: Optional[bool] = Field(
        description='Whether automatic management of the account is enabled or not', default=None
    )
    manual_management_reason: Optional[str] = Field(description='The reason for disabling automatic management', default=None)
    last_modified_time: Optional[int] = Field(description='Last time the management properties were modified', default=None)


class ArkPCloudAccountRemoteMachinesAccess(ArkCamelizedModel):
    remote_machines: Optional[Union[List[str], str]] = Field(
        description='Remote machines the access of this account is allowed', default=None
    )
    access_restricted_to_remote_machines: Optional[bool] = Field(
        description='Whether the access is only restricted to those remote machines',
        default=None,
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
    platform_id: Optional[str] = Field(description='Platform id to relate the account to', default=None)
    user_name: Optional[str] = Field(description='Username of the account', default=None)
    address: Optional[str] = Field(description='Address of the account', default=None)
    secret_type: Optional[ArkPCloudAccountSecretType] = Field(description='Type of the secret of the account', default=None)
    platform_account_properties: Optional[Dict[str, Any]] = Field(
        description='Different properties related to the platform the account is related to',
        default=None,
    )
    secret_management: Optional[ArkPCloudAccountSecretManagement] = Field(description='Secret mgmt related properties', default=None)
    remote_machines_access: Optional[ArkPCloudAccountRemoteMachinesAccess] = Field(
        description='Remote machines access related properties', default=None
    )


class ArkPCloudAccount(ArkPCloudBaseAccount):
    id: str = Field(description='ID of the account')
    status: Optional[str] = Field(description='Status of the account', default=None)
    created_time: Optional[int] = Field(description='Creation time of the account', default=None)
    category_modification_time: Optional[int] = Field(description='Category modification time of the account', default=None)
