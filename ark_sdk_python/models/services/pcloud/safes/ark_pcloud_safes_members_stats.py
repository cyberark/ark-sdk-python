from typing import Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.common import ArkCountedValues
from ark_sdk_python.models.services.pcloud.safes.ark_pcloud_safe_member import ArkPCloudSafeMemberPermissionSet, ArkPCloudSafeMemberType


class ArkPCloudSafeMembersStats(ArkModel):
    safe_members_count: int = Field(description='Overall members count')
    safe_members_permission_sets: Dict[ArkPCloudSafeMemberPermissionSet, ArkCountedValues] = Field(description='Members per permission set')
    safe_members_types_count: Dict[ArkPCloudSafeMemberType, int] = Field(description='Members count per type')


class ArkPCloudSafesMembersStats(ArkModel):
    safe_members_stats: Dict[str, ArkPCloudSafeMembersStats] = Field(description='Safe members stats per safe')
