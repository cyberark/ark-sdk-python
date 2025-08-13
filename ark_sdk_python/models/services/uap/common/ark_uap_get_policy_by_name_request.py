from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkUAPGetPolicyByNameRequest(ArkModel):
    policy_name: str = Field(description='Policy name to be retrieved')
