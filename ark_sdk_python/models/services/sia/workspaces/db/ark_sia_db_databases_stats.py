from typing import Dict

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_auth_method import ArkSIADBAuthMethodType
from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_provider import (
    ArkSIADBDatabaseEngineType,
    ArkSIADBDatabaseFamilyType,
    ArkSIADBDatabaseWorkspaceType,
)
from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_warning import ArkSIADBWarning


class ArkSIADBDatabasesStats(ArkModel):
    databases_count: int = Field(description='Databases overall count')
    databases_without_secret_count: int = Field(description='Databases who does not have any secret attached to them')
    databases_without_certificates_count: int = Field(description='Databases who does not have any certificates attached to them')
    databases_count_by_engine: Dict[ArkSIADBDatabaseEngineType, int] = Field(description='Databases count per engine type')
    databases_count_by_family: Dict[ArkSIADBDatabaseFamilyType, int] = Field(description='Databases count per family type')
    databases_count_by_workspace: Dict[ArkSIADBDatabaseWorkspaceType, int] = Field(description='Databases count per workspace type')
    databases_count_by_auth_method: Dict[ArkSIADBAuthMethodType, int] = Field(description='Databases count per auth type')
    databases_count_by_warning: Dict[ArkSIADBWarning, int] = Field(description='Databases count per warning type')
