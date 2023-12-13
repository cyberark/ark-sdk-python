from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkDPALoadPolicies(ArkModel):
    override: bool = Field(description='Whether to override existing policies', default=False)
