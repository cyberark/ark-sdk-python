from pydantic import Field

from ark_sdk_python.models import ArkTitleizedModel


class ArkIdentityPolicyInfo(ArkTitleizedModel):
    id: str = Field(description='ID of the policy', alias='ID')
    description: str = Field(description='Description of the policy')
    enable_compliant: bool = Field(description='Enable policy compliant')
    link_type: str = Field(description='Type of policy link')
    policy_set: str = Field(description="Policy set name")
