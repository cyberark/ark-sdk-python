from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityDisablePolicy(ArkModel):
    policy_name: str = Field(description='Policy to disable')
