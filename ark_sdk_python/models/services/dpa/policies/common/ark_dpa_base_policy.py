from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.dpa.policies.common.ark_dpa_rule_status import ArkDPARuleStatus


class ArkDPABasePolicy(ArkCamelizedModel):
    policy_id: Optional[str] = Field(description='ID of the policy')
    policy_name: str = Field(description='Name of the policy')
    status: ArkDPARuleStatus = Field(description='Status of the policy')
    description: Optional[str] = Field(description='Description of the policy')
    start_date: Optional[str] = Field(description='Start date of the policy')
    end_date: Optional[str] = Field(description='End date of the policy')
