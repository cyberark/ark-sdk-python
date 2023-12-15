from pydantic import Field, validator

from ark_sdk_python.models.common import ArkProtocolType
from ark_sdk_python.models.common.ark_workspace_type import ArkWorkspaceType
from ark_sdk_python.models.services.dpa.policies.common.ark_dpa_base_authorization_rule import ArkDPABaseAuthorizationRule
from ark_sdk_python.models.services.dpa.policies.common.ark_dpa_base_connection_information import ArkDPABaseConnectionInformation
from ark_sdk_python.models.services.dpa.policies.vm.ark_dpa_vm_connection_data import ArkDPAVMProvidersConnectionDict


class ArkDPAVMConnectionInformation(ArkDPABaseConnectionInformation):
    connect_as: ArkDPAVMProvidersConnectionDict = Field(description='In which fashion the connection is made')

    # pylint: disable=no-self-use,no-self-argument
    @validator('connect_as')
    def validate_connect_as(cls, val):
        for k, v in val.items():
            if ArkWorkspaceType(k) not in [ArkWorkspaceType.AWS, ArkWorkspaceType.AZURE, ArkWorkspaceType.GCP, ArkWorkspaceType.ONPREM]:
                raise ValueError('Invalid Platform / Workspace Type')
            for k2 in v.keys():
                if ArkProtocolType(k2) not in [
                    ArkProtocolType.SSH,
                    ArkProtocolType.RDP,
                    ArkProtocolType.SFTP,
                    ArkProtocolType.SCP,
                    ArkProtocolType.HTTPS,
                ]:
                    raise ValueError('Invalid connection type')
        return val


class ArkDPAVMAuthorizationRule(ArkDPABaseAuthorizationRule):
    connection_information: ArkDPAVMConnectionInformation = Field(description='Rule information on how access is made')
