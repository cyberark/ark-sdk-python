from pydantic import Field, field_validator

from ark_sdk_python.models.common import ArkProtocolType
from ark_sdk_python.models.common.ark_workspace_type import ArkWorkspaceType
from ark_sdk_python.models.services.sia.policies.common.ark_sia_base_authorization_rule import ArkSIABaseAuthorizationRule
from ark_sdk_python.models.services.sia.policies.common.ark_sia_base_connection_information import ArkSIABaseConnectionInformation
from ark_sdk_python.models.services.sia.policies.vm.ark_sia_vm_connection_data import ArkSIAVMProvidersConnectionDict


class ArkSIAVMConnectionInformation(ArkSIABaseConnectionInformation):
    connect_as: ArkSIAVMProvidersConnectionDict = Field(description='In which fashion the connection is made')

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('connect_as', mode="before")
    @classmethod
    def validate_connect_as(cls, val):
        if val is not None:
            new_val = {}
            for k, v in val.items():
                if ArkWorkspaceType(k) not in [
                    ArkWorkspaceType.AWS,
                    ArkWorkspaceType.AZURE,
                    ArkWorkspaceType.GCP,
                    ArkWorkspaceType.ONPREM,
                ]:
                    raise ValueError('Invalid Platform / Workspace Type')
                new_val2 = {}
                for k2 in v.keys():
                    if ArkProtocolType(k2) not in [
                        ArkProtocolType.SSH,
                        ArkProtocolType.RDP,
                        ArkProtocolType.SFTP,
                        ArkProtocolType.SCP,
                        ArkProtocolType.HTTPS,
                    ]:
                        raise ValueError('Invalid connection type')
                    new_val2[ArkProtocolType(k2)] = v[k2]
                new_val[ArkWorkspaceType(k)] = new_val2
            return new_val
        return val


class ArkSIAVMAuthorizationRule(ArkSIABaseAuthorizationRule):
    connection_information: ArkSIAVMConnectionInformation = Field(description='Rule information on how access is made')
