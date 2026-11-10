from typing import Optional

from pydantic import Field, field_validator

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.common import ArkWorkspaceType
from ark_sdk_python.models.services.cmgr.ark_cmgr_component import ArkCmgrComponentStatusCode


class ArkCmgrConnectorsFilter(ArkCamelizedModel):
    connector_status: Optional[ArkCmgrComponentStatusCode] = Field(default=None, description='Filter by connector status')
    component_status: Optional[ArkCmgrComponentStatusCode] = Field(default=None, description='Filter by any of the components status')
    platform_type: Optional[ArkWorkspaceType] = Field(default=None, description='Filter by platform type of the connector')
    connector_version: Optional[str] = Field(default=None, description='Filter by the version of the connector')
    connector_pool_id: Optional[str] = Field(default=None, description='Filter connectors by connector pool id')
    limit: Optional[int] = Field(default=None, description='Limit results')
    cursor: Optional[str] = Field(default=None, description='Cursor placement of the result')
    sort: Optional[str] = Field(default=None, description='Sort results by key')

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('platform_type', mode="before")
    @classmethod
    def validate_platform_type(cls, val):
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
