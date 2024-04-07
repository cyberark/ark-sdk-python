from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityEnablePolicy(ArkModel):
    policy_name: str = Field(description='Policy to enable')
