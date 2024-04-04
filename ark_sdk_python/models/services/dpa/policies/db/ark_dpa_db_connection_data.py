from enum import Enum
from typing import Dict, List, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel
from ark_sdk_python.models.services.dpa.policies.db.ark_dpa_db_enums import ArkDPADBMongoDatabaseBuiltinRole, ArkDPADBMongoGlobalBuiltinRole


class ArkDPADBBaseAuth(ArkCamelizedModel):
    pass


class ArkDPADBResourceIdentifierType(str, Enum):
    RESOURCE = 'resource'
    TAG = 'tag'


class ArkDPADBAppliedTo(ArkCamelizedModel):
    name: str = Field(description='Name of the resource to apply the auth to')
    type: ArkDPADBResourceIdentifierType = Field(description='Type of the resource')


class ArkDPADBLDAPAuth(ArkDPADBBaseAuth):
    assign_groups: List[str] = Field(description='LDAP groups to assign the ephemeral user to')
    applied_to: Optional[List[ArkDPADBAppliedTo]] = Field(description='Which resources to apply to')


class ArkDPADBLocalDBAuth(ArkDPADBBaseAuth):
    roles: List[str] = Field(description='Local DB roles to assign the ephemeral user to')
    applied_to: Optional[List[ArkDPADBAppliedTo]] = Field(description='Which resources to apply to')


class ArkDPADBOracleDBAuth(ArkDPADBBaseAuth):
    roles: List[str] = Field(description='Local DB roles to assign the ephemeral user to')
    applied_to: Optional[List[ArkDPADBAppliedTo]] = Field(description='Which resources to apply to')
    dba_role: bool = Field(description='Whether to apply to the ephemeral user the DBA role', default=False)
    sysdba_role: bool = Field(description='Whether to apply to the ephemeral user the SYSDBA role', default=False)
    sysoper_role: bool = Field(description='Whether to apply to the ephemeral user the SYSOPER role', default=False)


class ArkDPADBMongoDBAuth(ArkDPADBBaseAuth):
    global_builtin_roles: List[ArkDPADBMongoGlobalBuiltinRole] = Field(
        description='Global builtin roles across all databases', default_factory=list
    )
    database_builtin_roles: Dict[str, List[ArkDPADBMongoDatabaseBuiltinRole]] = Field(
        description='Per database builtin roles', default_factory=dict
    )
    database_custom_roles: Dict[str, List[str]] = Field(description='Custom per database roles', default_factory=dict)
    applied_to: Optional[List[ArkDPADBAppliedTo]] = Field(description='Which resources to apply to')


class ArkDPADBConnectAs(ArkCamelizedModel):
    ldap_auth: Optional[List[ArkDPADBLDAPAuth]] = Field(description='LDAP related authentication, only applies to MSSQL DB')
    db_auth: Optional[List[ArkDPADBLocalDBAuth]] = Field(
        description='Local DB related authentication, only applies to MySQL / MariaDB / Postgres'
    )
    oracle_auth: Optional[List[ArkDPADBOracleDBAuth]] = Field(description='Oracle DB related authentication, only applies to Oracle')
    mongo_auth: Optional[List[ArkDPADBMongoDBAuth]] = Field(description='Mongo DB related authentication, only applies to Mongo')
