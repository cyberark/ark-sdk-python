from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.sia.policies.common.ark_sia_rule_status import ArkSIARuleStatus


class ArkSIABasePolicy(ArkCamelizedModel):
    policy_id: Optional[str] = Field(default=None, description='ID of the policy')
    policy_name: str = Field(description='Name of the policy')
    status: ArkSIARuleStatus = Field(description='Status of the policy')
    description: Optional[str] = Field(default=None, description='Description of the policy')
    start_date: Optional[str] = Field(default=None, description='Start date of the policy')
    end_date: Optional[str] = Field(default=None, description='End date of the policy')
