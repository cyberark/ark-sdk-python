from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.services.dpa.workspaces.db.ark_dpa_db_provider import (
    ArkDPADBDatabaseEngineType,
    ArkDPADBDatabaseFamilyType,
    ArkDPADBDatabaseWorkspaceType,
)
from ark_sdk_python.models.services.dpa.workspaces.db.ark_dpa_db_tag import ArkDPADBTag
from ark_sdk_python.models.services.dpa.workspaces.db.ark_dpa_db_warning import ArkDPADBWarning


class ArkDPADBDatabasesFilter(ArkModel):
    name: Optional[str] = Field(description='Name of the database to filter on')
    provider_family: Optional[ArkDPADBDatabaseFamilyType] = Field(description='List filter by family')
    provider_engine: Optional[ArkDPADBDatabaseEngineType] = Field(description='List filter by engine')
    provider_workspace: Optional[ArkDPADBDatabaseWorkspaceType] = Field(description='List filter by workspace')
    tags: Optional[List[ArkDPADBTag]] = Field(description='List filter by tags')
    db_warnings_filter: Optional[ArkDPADBWarning] = Field(description='Filter by databases who are with warnings / incomplete')
