from typing import Dict

from pydantic import Field, validator

from ark_sdk_python.models.common import ArkWorkspaceType
from ark_sdk_python.models.services.dpa.policies.common.ark_dpa_base_policies_stats import ArkDPABasePoliciesStats


class ArkDPAVMPoliciesStats(ArkDPABasePoliciesStats):
    policies_count_per_provider: Dict[ArkWorkspaceType, int] = Field(description='Policies count per VM platform')

    # pylint: disable=no-self-use,no-self-argument
    @validator('policies_count_per_provider')
    def validate_policies_count_per_provider(cls, val):
        for k in val.keys():
            if ArkWorkspaceType(k) not in [
                ArkWorkspaceType.AWS,
                ArkWorkspaceType.AZURE,
                ArkWorkspaceType.GCP,
                ArkWorkspaceType.ONPREM,
            ]:
                raise ValueError('Invalid Platform / Workspace Type')
        return val
