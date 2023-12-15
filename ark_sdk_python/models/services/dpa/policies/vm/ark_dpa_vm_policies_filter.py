from typing import List, Optional

from pydantic import Field, validator

from ark_sdk_python.models.common import ArkWorkspaceType
from ark_sdk_python.models.services.dpa.policies.common.ark_dpa_base_policies_filter import ArkDPABasePoliciesFilter


class ArkDPAVMPoliciesFilter(ArkDPABasePoliciesFilter):
    providers: Optional[List[ArkWorkspaceType]] = Field(description='Filter by policies with given cloud providers')

    # pylint: disable=no-self-use,no-self-argument
    @validator('providers')
    def validate_providers(cls, val):
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
