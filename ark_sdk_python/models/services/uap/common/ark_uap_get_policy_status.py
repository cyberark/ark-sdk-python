from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkUAPGetPolicyStatus(ArkCamelizedModel):
    policy_id: Optional[str] = Field(default=None, description='Policy id to get the status for')
    policy_name: Optional[str] = Field(default=None, description='Policy name to get the status for')
