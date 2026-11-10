from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.cmgr.ark_cmgr_component import ArkCmgrComponentStatusCode


class ArkCmgrComponentsFilter(ArkModel):
    component_name: Optional[str] = Field(default=None, description='Filter by name of the component')
    component_status: Optional[ArkCmgrComponentStatusCode] = Field(default=None, description='Filter by status of the component')
    version: Optional[str] = Field(default=None, description='Filter by version of the component')
    upgrade_version: Optional[str] = Field(default=None, description='Filter by upgradable version of the component')
    limit: Optional[int] = Field(default=None, description='Limit results')
    cursor: Optional[str] = Field(default=None, description='Cursor placement of the result')
    sort: Optional[str] = Field(default=None, description='Sort results by key')
