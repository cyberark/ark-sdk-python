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
    membership_expiration_date: Optional[datetime] = Field(description='What is the member expiration date to update', default=None)
    permissions: Optional[ArkPCloudSafeMemberPermissions] = Field(
        description='Permissions of the safe member on the safe to update', default=None
    )
    permission_set: Optional[ArkPCloudSafeMemberPermissionSet] = Field(description='Predefined permission set to update to', default=None)
