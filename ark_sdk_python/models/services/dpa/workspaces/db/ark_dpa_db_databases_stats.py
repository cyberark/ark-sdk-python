from typing import Dict

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.services.dpa.workspaces.db.ark_dpa_db_provider import (
    ArkDPADBDatabaseEngineType,
    ArkDPADBDatabaseFamilyType,
    ArkDPADBDatabaseWorkspaceType,
)
from ark_sdk_python.models.services.dpa.workspaces.db.ark_dpa_db_warning import ArkDPADBWarning


class ArkDPADBDatabasesStats(ArkModel):
    databases_count: int = Field(description='Databases overall count')
    databases_without_secret_count: int = Field(description='Databases who does not have any secret attached to them')
    databases_without_certificates_count: int = Field(description='Databases who does not have any certificates attached to them')
    databases_count_by_engine: Dict[ArkDPADBDatabaseEngineType, int] = Field(description='Databases count per engine type')
    databases_count_by_family: Dict[ArkDPADBDatabaseFamilyType, int] = Field(description='Databases count per family type')
    databases_count_by_workspace: Dict[ArkDPADBDatabaseWorkspaceType, int] = Field(description='Databases count per workspace type')
    databases_count_by_warning: Dict[ArkDPADBWarning, int] = Field(description='Databases count per warning type')
