from typing import Dict

from pydantic import Field, field_validator

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.common import ArkOsType, ArkWorkspaceType


class ArkSIAConnectorsStats(ArkModel):
    connectors_count: int = Field(description='Total connectors count')
    upgradable_connectors_count: int = Field(description='Total upgradable connectors count')
    connectors_count_by_os: Dict[ArkOsType, int] = Field(description='Connectors count by os')
    connectors_count_by_platform: Dict[ArkWorkspaceType, int] = Field(description='Connectors count by platform')
    connectors_count_by_status_codes: Dict[str, int] = Field(description='Connectors count by status codes')

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('connectors_count_by_platform', mode="before")
    @classmethod
    def validate_connectors_count_by_platform(cls, val):
        if val is not None:
            new_val = []
            for workspace in val:
                if ArkWorkspaceType(workspace) not in [
                    ArkWorkspaceType.AWS,
                    ArkWorkspaceType.AZURE,
                    ArkWorkspaceType.GCP,
                    ArkWorkspaceType.ONPREM,
                    ArkWorkspaceType.FAULT,
                ]:
                    raise ValueError('Invalid Platform / Workspace Type')
                new_val.append(ArkWorkspaceType(workspace))
            return new_val
        return val
