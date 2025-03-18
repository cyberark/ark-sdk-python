from typing import List, Optional

from pydantic import Field, field_validator

from ark_sdk_python.models.common import ArkWorkspaceType
from ark_sdk_python.models.services.sia.policies.common.ark_sia_base_policy import ArkSIABasePolicy
from ark_sdk_python.models.services.sia.policies.vm.ark_sia_vm_authorization_rule import ArkSIAVMAuthorizationRule
from ark_sdk_python.models.services.sia.policies.vm.ark_sia_vm_policies_workspace_type_serializer import (
    serialize_sia_vm_policies_workspace_type,
)
from ark_sdk_python.models.services.sia.policies.vm.ark_sia_vm_providers import ArkSIAVMProvidersDict


class ArkSIAVMPolicy(ArkSIABasePolicy):
    providers_data: Optional[ArkSIAVMProvidersDict] = Field(default=None, description='Cloud providers info of the policy')
    user_access_rules: Optional[List[ArkSIAVMAuthorizationRule]] = Field(default=None, description='Authorization rules of the policy')
    updated_on: Optional[str] = Field(default=None, description='Update time of the policy')
    updated_by: Optional[str] = Field(default=None, description='Who updated the policy')
    created_on: Optional[str] = Field(default=None, description='Creation time of the policy')
    created_by: Optional[str] = Field(default=None, description='Who created the policy')

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('providers_data', mode="before")
    @classmethod
    def validate_providers_data(cls, val):
        if val is not None:
            new_val = {}
            for k in val.keys():
                if isinstance(val[k], dict):
                    val[k]['providerName'] = serialize_sia_vm_policies_workspace_type(ArkWorkspaceType(k))
                else:
                    val[k].provider_name = serialize_sia_vm_policies_workspace_type(ArkWorkspaceType(k))
                if ArkWorkspaceType(k) not in [
                    ArkWorkspaceType.AWS,
                    ArkWorkspaceType.AZURE,
                    ArkWorkspaceType.GCP,
                    ArkWorkspaceType.ONPREM,
                ]:
                    raise ValueError('Invalid Platform / Workspace Type')
                new_val[ArkWorkspaceType(k)] = val[k]
            return new_val
        return val
