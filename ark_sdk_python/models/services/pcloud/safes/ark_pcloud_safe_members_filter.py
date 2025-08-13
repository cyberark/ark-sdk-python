from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.pcloud.safes.ark_pcloud_safe_member import ArkPCloudSafeMemberType


class ArkPCloudSafeMembersFilters(ArkModel):
    safe_id: str = Field(description='Which safe id to filter the members on')
    search: Optional[str] = Field(default=None, description='Search by string')
    sort: Optional[str] = Field(default=None, description='Sort results by given key')
    offset: Optional[int] = Field(default=None, description='Offset to the safe members list')
    limit: Optional[int] = Field(default=None, description='Limit of results')
    member_type: Optional[ArkPCloudSafeMemberType] = Field(default=None, description='Filter by type of safe member')
