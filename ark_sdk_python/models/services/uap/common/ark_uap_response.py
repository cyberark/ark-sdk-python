from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkUAPResponse(ArkCamelizedModel):
    policy_id: str = Field(description='Policy id')
