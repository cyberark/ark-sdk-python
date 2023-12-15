from typing import Dict, List, Union

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.common import ArkProtocolType, ArkWorkspaceType


class ArkDPAVMConnectionMethodData(ArkCamelizedModel):
    pass


class ArkDPAVMLocalEphemeralUserConnectionMethodData(ArkDPAVMConnectionMethodData):
    assign_groups: List[str] = Field(description='Predefined assigned groups of the user', default_factory=list)


class ArkDPAVMRDPLocalEphemeralUserConnectionData(ArkCamelizedModel):
    local_ephemeral_user: ArkDPAVMLocalEphemeralUserConnectionMethodData = Field(description='Local ephemeral user method related data')


ArkDPAVMConnectionDataType = Union[str, ArkDPAVMRDPLocalEphemeralUserConnectionData]
ArkDPAVMConnectionProtocolDict = Dict[ArkProtocolType, ArkDPAVMConnectionDataType]
ArkDPAVMProvidersConnectionDict = Dict[ArkWorkspaceType, ArkDPAVMConnectionProtocolDict]
