from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkPCloudListSafeMembers(ArkModel):
    safe_id: str = Field(description='Which safe id to list the members on')
