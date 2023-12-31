from typing import Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.dpa.policies.common.ark_dpa_rule_status import ArkDPARuleStatus


class ArkDPABasePoliciesStats(ArkModel):
    policies_count: int = Field(description='Overall count of policies')
    policies_count_per_status: Dict[ArkDPARuleStatus, int] = Field(description='Policies count per rule status')
