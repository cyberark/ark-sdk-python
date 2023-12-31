from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.dpa.policies.common.ark_dpa_rule_status import ArkDPARuleStatus


class ArkDPABasePolicyListItem(ArkCamelizedModel):
    policy_id: str = Field(description='ID of the policy')
    policy_name: str = Field(description='Name of the policy')
    status: ArkDPARuleStatus = Field(description='Status of the policy')
    description: Optional[str] = Field(description='Description of the policy')
    updated_on: str = Field(description='Last update time of the policy')
    rule_names: Optional[List[str]] = Field(description='Names of the authorization rules of the policy')
