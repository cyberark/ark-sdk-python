from typing import List, Optional

from pydantic import Field, validator

from ark_sdk_python.models.common import ArkWorkspaceType
from ark_sdk_python.models.services.dpa.policies.common.ark_dpa_base_policy_list_item import ArkDPABasePolicyListItem


class ArkDPAVMPolicyListItem(ArkDPABasePolicyListItem):
    platforms: Optional[List[ArkWorkspaceType]] = Field(description='Names of the platforms of the policy')

    # pylint: disable=no-self-use,no-self-argument
    @validator('platforms')
    def validate_platforms(cls, val):
        if val is not None:
            for plat in val:
                if ArkWorkspaceType(plat) not in [
                    ArkWorkspaceType.AWS,
                    ArkWorkspaceType.AZURE,
                    ArkWorkspaceType.GCP,
                    ArkWorkspaceType.ONPREM,
                ]:
                    raise ValueError('Invalid Platform / Workspace Type')
        return val
