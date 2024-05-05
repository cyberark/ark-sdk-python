from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudGetSafeMembersStats(ArkModel):
    safe_id: str = Field(description='Safe url id to get the members stats for')
