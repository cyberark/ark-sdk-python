from typing import List, Optional

from pydantic import Field, root_validator, validator

from ark_sdk_python.models.ark_model import ArkCamelizedModel
from ark_sdk_python.models.common.ark_workspace_type import ArkWorkspaceType
from ark_sdk_python.models.services.dpa.workspaces.db.ark_dpa_db_provider import ArkDPADBDatabaseEngineType
from ark_sdk_python.models.services.dpa.workspaces.db.ark_dpa_db_tag import ArkDPADBTag


class ArkDPADBUpdateDatabase(ArkCamelizedModel):
    id: Optional[int] = Field(description='Database id to update')
    name: Optional[str] = Field(description='Database name to update')
    new_name: Optional[str] = Field(description='New name for the database')
    network_name: Optional[str] = Field(description='Name of the network the database resides in', default='ON-PREMISE')
    platform: Optional[ArkWorkspaceType] = Field(description='Platform of the database, as in, where it resides')
    auth_database: str = Field(description='Authentication database used, most commonly used with mongodb', default='admin')
    services: Optional[List[str]] = Field(description='Services related to the database, most commonly used with oracle')
    domain: Optional[str] = Field(description='The domain the DB resides in')
    domain_controller_name: Optional[str] = Field(description='Domain controller name associated to this database')
    domain_controller_netbios: Optional[str] = Field(description='Domain controller netbios associated to this database')
    domain_controller_use_ldaps: bool = Field(description='Whether to work with LDAP secure or not', default=False)
    domain_controller_enable_certificate_validation: bool = Field(
        description='Whether to enforce certificate validation on TLS comm to the DC', default=True
    )
    domain_controller_ldaps_certificate: Optional[str] = Field(description='Certificate id to use for the domain controller TLS comm')
    provider_engine: Optional[ArkDPADBDatabaseEngineType] = Field(
        description='Provider engine, will be later deduced to the identifer of the provider'
    )
    enable_certificate_validation: bool = Field(description='Whether to enable and enforce certificate validation', default=True)
    certificate: Optional[str] = Field(description='Certificate id used for this database that resides in the certificates service')
    read_write_endpoint: Optional[str] = Field(description='Read write endpoint of the database')
    read_only_endpoint: Optional[str] = Field(description='Optionally, a read only endpoint of the database')
    port: Optional[int] = Field(description='Port of the database, if not given, the default one will be used')
    secret_id: Optional[str] = Field(description='Secret identifier stored in the secret service related to this database')
    tags: Optional[List[ArkDPADBTag]] = Field(description='Tags for the database')

    # pylint: disable=no-self-use,no-self-argument
    @root_validator
    def validate_either(cls, values):
        if 'id' not in values and 'name' not in values:
            raise ValueError('Either id or name needs to be provided')
        return values

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
