from typing import List, Optional

from pydantic import Field, field_validator

from ark_sdk_python.models.common.ark_workspace_type import ArkWorkspaceType
from ark_sdk_python.models.services.sia.policies.common.ark_sia_base_add_policy import ArkSIABaseAddPolicy
from ark_sdk_python.models.services.sia.policies.vm.ark_sia_vm_authorization_rule import ArkSIAVMAuthorizationRule
from ark_sdk_python.models.services.sia.policies.vm.ark_sia_vm_policies_workspace_type_serializer import (
    serialize_sia_vm_policies_workspace_type,
)
from ark_sdk_python.models.services.sia.policies.vm.ark_sia_vm_providers import ArkSIAVMProvidersDict


class ArkSIAVMAddPolicy(ArkSIABaseAddPolicy):
    providers_data: Optional[ArkSIAVMProvidersDict] = Field(
        default=None,
        description='Workspaces / cloud providers data per type of cloud provider, '
        'for example for AWS, how to filter ec2 instances to connect to',
    )
    user_access_rules: Optional[List[ArkSIAVMAuthorizationRule]] = Field(
        default=None,
        description='Rules describing how and who will be able to connect to the target instances filtered by the cloud providers',
    )

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
                if ArkWorkspaceType(k) not in [ArkWorkspaceType.AWS, ArkWorkspaceType.AZURE, ArkWorkspaceType.GCP, ArkWorkspaceType.ONPREM]:
                    raise ValueError('Invalid Platform / Workspace Type')
                new_val[ArkWorkspaceType(k)] = val[k]
            return new_val
        return val
