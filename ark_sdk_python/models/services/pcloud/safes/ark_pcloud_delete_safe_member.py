from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudDeleteSafeMember(ArkModel):
    safe_id: str = Field(description='Safe url id to remove the member from')
    member_name: str = Field(description='Name of the member to remove')
