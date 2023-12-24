from typing import List, Optional

from pydantic import Field, validator

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.common.ark_workspace_type import ArkWorkspaceType
from ark_sdk_python.models.services.dpa.workspaces.db.ark_dpa_db_provider import ArkDPADBDatabaseProvider


class ArkDPADBDatabaseInfo(ArkModel):
    id: int = Field(description='ID of the database target that can be referenced in operations')
    name: str = Field(description='Name of the database, often referenced in policies and other APIs')
    enable_certificate_validation: bool = Field(description='Whether to enable and enforce certificate validation', default=True)
    certificate: Optional[str] = Field(description='Certificate id related to this database')
    services: List[str] = Field(description='Services related to the database, most commonly used with oracle', default_factory=list)
    secret_id: Optional[str] = Field(description='Secret identifier stored in the secret service related to this database')
    platform: Optional[ArkWorkspaceType] = Field(description='Platform of the database, as in, where it resides')
    provider_info: ArkDPADBDatabaseProvider = Field(description='Provider details')

    # pylint: disable=no-self-use,no-self-argument
    @validator('platform')
    def validate_workspace_type(cls, val):
        if val and ArkWorkspaceType(val) not in [
            ArkWorkspaceType.AWS,
            ArkWorkspaceType.AZURE,
            ArkWorkspaceType.GCP,
            ArkWorkspaceType.ONPREM,
        ]:
            raise ValueError('Invalid Platform / Workspace Type')
        return val


class ArkDPADBDatabaseInfoList(ArkModel):
    items: List[ArkDPADBDatabaseInfo] = Field(description='The actual databases')
    total_count: int = Field(description='Total count of databases')
