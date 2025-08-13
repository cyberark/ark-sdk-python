from datetime import datetime
from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.pcloud.safes.ark_pcloud_safe_member import (
    ArkPCloudSafeMemberPermissions,
    ArkPCloudSafeMemberPermissionSet,
)


class ArkPCloudUpdateSafeMember(ArkCamelizedModel):
    safe_id: str = Field(description='Safe url id to update the member on')
    member_name: str = Field(description='Name of the member to update')
    membership_expiration_date: Optional[datetime] = Field(default=None, description='What is the member expiration date to update')
    permissions: Optional[ArkPCloudSafeMemberPermissions] = Field(
        default=None, description='Permissions of the safe member on the safe to update'
    )
    permission_set: Optional[ArkPCloudSafeMemberPermissionSet] = Field(default=None, description='Predefined permission set to update to')
