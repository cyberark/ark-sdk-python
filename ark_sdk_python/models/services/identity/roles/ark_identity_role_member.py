from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.identity.directories.ark_identity_entity import ArkIdentityEntityType


class ArkIdentityRoleMember(ArkModel):
    member_id: str = Field(description='ID of the mmeber')
    member_name: str = Field(description='Name of the member')
    member_type: ArkIdentityEntityType = Field(description='Type of the member')
