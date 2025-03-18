from typing import List, Optional

from pydantic import Field, field_validator

from ark_sdk_python.models.common import ArkWorkspaceType
from ark_sdk_python.models.services.sia.policies.common.ark_sia_base_policy_list_item import ArkSIABasePolicyListItem


class ArkSIAVMPolicyListItem(ArkSIABasePolicyListItem):
    platforms: Optional[List[ArkWorkspaceType]] = Field(default=None, description='Names of the platforms of the policy')

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('platforms', mode="before")
    @classmethod
    def validate_platforms(cls, val):
        if val is not None:
            new_val = []
            for plat in val:
                parsed_plat = ArkWorkspaceType(plat)
                if parsed_plat not in [
                    ArkWorkspaceType.AWS,
                    ArkWorkspaceType.AZURE,
                    ArkWorkspaceType.GCP,
                    ArkWorkspaceType.ONPREM,
                ]:
                    raise ValueError('Invalid Platform / Workspace Type')
                new_val.append(parsed_plat)
            return new_val
        return val
