from typing import List, Optional

from pydantic import Field, field_validator
from typing_extensions import Literal

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.common import ArkOsType, ArkWorkspaceType


class ArkSIAConnectorsFilter(ArkModel):
    accounts: Optional[List[str]] = Field(default=None, description='Filter by list of accounts')
    regions: Optional[List[str]] = Field(default=None, description='Filter by list of regions')
    host_types: Optional[List[ArkWorkspaceType]] = Field(default=None, description='Filter by platform types')
    only_upgradable_connectors: Optional[bool] = Field(default=None, description='Filter only upgradable connectors')
    only_latest_version_connectors: Optional[bool] = Field(default=None, description='Filter only latest versions connectors')
    only_connectors_with_sessions: Optional[bool] = Field(default=None, description='Filter only connectors with active sessions')
    status_codes: Optional[List[Literal['INACTIVE', 'ACTIVE', 'DOWNLOADED', 'READY FOR MAINTENANCE', 'PREPARING FOR MAINTENANCE']]] = Field(
        default=None, description='Filter by list of status codes'
    )
    os_types: Optional[List[ArkOsType]] = Field(default=None, description='Filter by list of operating system types')

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('host_types', mode="before")
    @classmethod
    def validate_host_types(cls, val):
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
