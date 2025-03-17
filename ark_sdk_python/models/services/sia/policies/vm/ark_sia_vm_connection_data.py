from typing import Dict, List, Union

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.common import ArkProtocolType, ArkWorkspaceType


class ArkSIAVMConnectionMethodData(ArkCamelizedModel):
    pass


class ArkSIAVMLocalEphemeralUserConnectionMethodData(ArkSIAVMConnectionMethodData):
    assign_groups: List[str] = Field(description='Predefined assigned groups of the user', default_factory=list)


class ArkSIAVMRDPLocalEphemeralUserConnectionData(ArkCamelizedModel):
    local_ephemeral_user: ArkSIAVMLocalEphemeralUserConnectionMethodData = Field(description='Local ephemeral user method related data')


ArkSIAVMConnectionDataType = Union[str, ArkSIAVMRDPLocalEphemeralUserConnectionData]
ArkSIAVMConnectionProtocolDict = Dict[ArkProtocolType, ArkSIAVMConnectionDataType]
ArkSIAVMProvidersConnectionDict = Dict[ArkWorkspaceType, ArkSIAVMConnectionProtocolDict]
