from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIADeleteTargetSet(ArkModel):
    name: str = Field(description='Name of the target set to delete')
