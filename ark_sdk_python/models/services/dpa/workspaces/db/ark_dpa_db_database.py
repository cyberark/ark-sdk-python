from typing import List, Optional

from pydantic import Field, validator

from ark_sdk_python.models.ark_model import ArkCamelizedModel
from ark_sdk_python.models.common.ark_workspace_type import ArkWorkspaceType
from ark_sdk_python.models.services.dpa.workspaces.db.ark_dpa_db_provider import ArkDPADBDatabaseProvider
from ark_sdk_python.models.services.dpa.workspaces.db.ark_dpa_db_tag import ArkDPADBTag


class ArkDPADBDatabase(ArkCamelizedModel):
    id: Optional[int] = Field(description='ID of the database target that can be referenced in operations')
    name: str = Field(description='Name of the database, often referenced in policies and other APIs')
    network_name: str = Field(description='Name of the network the database resides in', default='OnPrem')
    platform: Optional[ArkWorkspaceType] = Field(description='Platform of the database, as in, where it resides')
    auth_database: str = Field(description='Authentication database used, most commonly used with mongodb', default='admin')
    services: List[str] = Field(description='Services related to the database, most commonly used with oracle', default_factory=list)
    domain: Optional[str] = Field(description='The domain the DB resides in')
    domain_controller_name: Optional[str] = Field(description='Domain controller name associated to this database')
    domain_controller_netbios: Optional[str] = Field(description='Domain controller netbios associated to this database')
    provider_details: Optional[ArkDPADBDatabaseProvider] = Field(description='Provider details related to the database')
    enable_certificate_validation: bool = Field(description='Whether to enable and enforce certificate validation', default=True)
    certificate: Optional[str] = Field(description='Certificate id used for this database that resides in the certificates service')
    read_write_endpoint: str = Field(description='Read write endpoint of the database')
    read_only_endpoint: Optional[str] = Field(description='Optionally, a read only endpoint of the database')
    port: Optional[int] = Field(description='Port of the database, if not given, the default one will be used')
    secret_id: Optional[str] = Field(description='Secret identifier stored in the secret service related to this database')
    tags: Optional[List[ArkDPADBTag]] = Field(description='Tags for the database')

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
