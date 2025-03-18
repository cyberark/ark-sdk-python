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
    search_in: Optional[str] = Field(description='Where to search the member in, vault or a domain', default=None)
    membership_expiration_date: Optional[datetime] = Field(description='What is the member expiration date', default=None)
    permissions: Optional[ArkPCloudSafeMemberPermissions] = Field(description='Permissions of the safe member on the safe', default=None)
    permission_set: ArkPCloudSafeMemberPermissionSet = Field(
        description='Predefined permission set to use', default=ArkPCloudSafeMemberPermissionSet.ReadOnly
    )
