from typing import List, Optional

from pydantic import Field, field_validator

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.common.ark_workspace_type import ArkWorkspaceType
from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_auth_method import ArkSIADBAuthMethodType
from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_database_target_service import ArkSIADBDatabaseTargetServiceTypes
from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_provider import ArkSIADBDatabaseProvider


class ArkSIADBDatabaseInfo(ArkModel):
    id: int = Field(description='ID of the database target that can be referenced in operations')
    name: str = Field(description='Name of the database, often referenced in policies and other APIs')
    enable_certificate_validation: bool = Field(description='Whether to enable and enforce certificate validation', default=True)
    certificate: Optional[str] = Field(default=None, description='Certificate id related to this database')
    services: List[ArkSIADBDatabaseTargetServiceTypes] = Field(
        description='Services related to the database, most commonly used with oracle/sql-server', default_factory=list
    )
    secret_id: Optional[str] = Field(default=None, description='Secret identifier stored in the secret service related to this database')
    platform: Optional[ArkWorkspaceType] = Field(default=None, description='Platform of the database, as in, where it resides')
    provider_info: ArkSIADBDatabaseProvider = Field(description='Provider details')
    configured_auth_method_type: Optional[ArkSIADBAuthMethodType] = Field(
        default=None, description='The target configured auth method type'
    )

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('platform', mode="before")
    @classmethod
    def validate_workspace_type(cls, val):
        if val is not None:
            if val and ArkWorkspaceType(val) not in [
                ArkWorkspaceType.AWS,
                ArkWorkspaceType.AZURE,
                ArkWorkspaceType.GCP,
                ArkWorkspaceType.ONPREM,
                ArkWorkspaceType.ATLAS,
            ]:
                raise ValueError('Invalid Platform / Workspace Type')
            return ArkWorkspaceType(val)
        return val


class ArkSIADBDatabaseInfoList(ArkModel):
    items: List[ArkSIADBDatabaseInfo] = Field(description='The actual databases')
    total_count: int = Field(description='Total count of databases')
