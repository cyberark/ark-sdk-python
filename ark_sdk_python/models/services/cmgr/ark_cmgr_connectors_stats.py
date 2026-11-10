from typing import Dict

from pydantic import Field, field_validator

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.common import ArkCountedValues, ArkOsType, ArkWorkspaceType
from ark_sdk_python.models.services.cmgr.ark_cmgr_component import ArkCmgrComponentStatusCode


class ArkCmgrConnectorsStats(ArkModel):
    connectors_count: int = Field(description='Overall connectors count')
    connectors_count_per_status: Dict[ArkCmgrComponentStatusCode, int] = Field(description='Connectors count by status code')
    connectors_count_per_platform: Dict[ArkWorkspaceType, int] = Field(description='Connectors count by platform type')
    connectors_count_per_os: Dict[ArkOsType, int] = Field(description='Connectors count by os type')
    upgradable_connectors: ArkCountedValues = Field(description='Upgradable connectors count and values')

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('connectors_count_per_platform', mode="before")
    @classmethod
    def validate_connectors_count_per_platform(cls, val):
        if val is not None:
            if ArkWorkspaceType(val) not in [
                ArkWorkspaceType.AWS,
                ArkWorkspaceType.AZURE,
                ArkWorkspaceType.GCP,
                ArkWorkspaceType.ONPREM,
                ArkWorkspaceType.UNKNOWN,
            ]:
                raise ValueError('Invalid Platform / Workspace Type')
            return ArkWorkspaceType(val)
        return val
