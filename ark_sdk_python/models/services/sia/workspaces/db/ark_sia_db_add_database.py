from typing import List, Optional

from pydantic import Field, field_validator

from ark_sdk_python.models.ark_model import ArkCamelizedModel
from ark_sdk_python.models.common.ark_workspace_type import ArkWorkspaceType
from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_auth_method import ArkSIADBAuthMethodType
from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_database_target_service import ArkSIADBDatabaseTargetServiceTypes
from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_provider import ArkSIADBDatabaseEngineType
from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_tag import ArkSIADBTag


class ArkSIADBAddDatabase(ArkCamelizedModel):
    name: str = Field(description='Name of the database, often referenced in policies and other APIs')
    network_name: str = Field(description='Name of the network the database resides in, defaulted to on premises', default='ON-PREMISE')
    platform: ArkWorkspaceType = Field(
        description='Platform of the database, as in, where it resides, defaulted to on premises', default=ArkWorkspaceType.ONPREM
    )
    auth_database: str = Field(description='Authentication database used, most commonly used with mongodb', default='admin')
    services: List[ArkSIADBDatabaseTargetServiceTypes] = Field(
        description='Services related to the database, most commonly used with oracle/sql-server', default_factory=list
    )
    domain: Optional[str] = Field(default=None, description='The domain the DB resides in')
    domain_controller_name: Optional[str] = Field(default=None, description='Domain controller name associated to this database')
    domain_controller_netbios: Optional[str] = Field(default=None, description='Domain controller netbios associated to this database')
    domain_controller_use_ldaps: bool = Field(description='Whether to work with LDAP secure or not', default=False)
    domain_controller_enable_certificate_validation: bool = Field(
        description='Whether to enforce certificate validation on TLS comm to the DC', default=True
    )
    domain_controller_ldaps_certificate: Optional[str] = Field(
        default=None, description='Certificate id to use for the domain controller TLS comm'
    )
    account: Optional[str] = Field(default=None, description='Account to be used for provider based databases such as atlas')
    provider_engine: ArkSIADBDatabaseEngineType = Field(
        description='Provider engine, will be later deduced to the identifer of the provider'
    )
    enable_certificate_validation: bool = Field(description='Whether to enable and enforce certificate validation', default=True)
    certificate: Optional[str] = Field(
        default=None, description='Certificate id used for this database that resides in the certificates service'
    )
    read_write_endpoint: Optional[str] = Field(description='Read write endpoint of the database', default='')
    read_only_endpoint: Optional[str] = Field(default=None, description='Optionally, a read only endpoint of the database')
    port: Optional[int] = Field(default=None, description='Port of the database, if not given, the default one will be used')
    secret_id: Optional[str] = Field(default=None, description='Secret identifier stored in the secret service related to this database')
    tags: Optional[List[ArkSIADBTag]] = Field(default=None, description='Tags for the database')
    configured_auth_method_type: Optional[ArkSIADBAuthMethodType] = Field(
        default=None, description='The target configured auth method type'
    )
    region: Optional[str] = Field(default=None, description='Region of the database, most commonly used with iam authentication')

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
