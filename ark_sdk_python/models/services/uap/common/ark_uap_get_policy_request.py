from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkUAPGetPolicyRequest(ArkModel):
    policy_id: str = Field(description='Policy id to be retrieved')
