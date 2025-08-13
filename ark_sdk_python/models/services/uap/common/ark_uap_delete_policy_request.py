from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkUAPDeletePolicyRequest(ArkModel):
    policy_id: str = Field(description='Policy id to be deleted')
