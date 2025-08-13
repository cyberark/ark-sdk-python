from datetime import datetime
from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.pcloud.safes.ark_pcloud_safe_member import (
    ArkPCloudSafeMemberPermissions,
    ArkPCloudSafeMemberPermissionSet,
    ArkPCloudSafeMemberType,
)


class ArkPCloudAddSafeMember(ArkCamelizedModel):
    safe_id: str = Field(description='Safe url id to add the member to')
    member_name: str = Field(description='Name of the member to add')
    member_type: ArkPCloudSafeMemberType = Field(description='Type of the member')
    search_in: Optional[str] = Field(default=None, description='Where to search the member in, vault or a domain')
    membership_expiration_date: Optional[datetime] = Field(default=None, description='What is the member expiration date')
    permissions: Optional[ArkPCloudSafeMemberPermissions] = Field(default=None, description='Permissions of the safe member on the safe')
    permission_set: ArkPCloudSafeMemberPermissionSet = Field(
        description='Predefined permission set to use', default=ArkPCloudSafeMemberPermissionSet.ReadOnly
    )
