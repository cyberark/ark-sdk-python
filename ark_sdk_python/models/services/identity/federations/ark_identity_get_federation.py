from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityGetFederation(ArkModel):
    federation_id: str = Field(description='The unique identifier of the federation to get')
