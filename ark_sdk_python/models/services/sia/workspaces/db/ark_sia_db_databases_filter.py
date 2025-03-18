from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_auth_method import ArkSIADBAuthMethodType
from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_provider import (
    ArkSIADBDatabaseEngineType,
    ArkSIADBDatabaseFamilyType,
    ArkSIADBDatabaseWorkspaceType,
)
from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_tag import ArkSIADBTag
from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_warning import ArkSIADBWarning


class ArkSIADBDatabasesFilter(ArkModel):
    name: Optional[str] = Field(default=None, description='Name of the database to filter on')
    provider_family: Optional[ArkSIADBDatabaseFamilyType] = Field(default=None, description='List filter by family')
    provider_engine: Optional[ArkSIADBDatabaseEngineType] = Field(default=None, description='List filter by engine')
    provider_workspace: Optional[ArkSIADBDatabaseWorkspaceType] = Field(default=None, description='List filter by workspace')
    auth_methods: Optional[List[ArkSIADBAuthMethodType]] = Field(default=None, description='Auth method types to filter on')
    tags: Optional[List[ArkSIADBTag]] = Field(default=None, description='List filter by tags')
    db_warnings_filter: Optional[ArkSIADBWarning] = Field(
        default=None, description='Filter by databases who are with warnings / incomplete'
    )
