from enum import Enum
from typing import Dict, List, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel
from ark_sdk_python.models.services.dpa.policies.db.ark_dpa_db_enums import (
    ArkDPADBMongoDatabaseBuiltinRole,
    ArkDPADBMongoGlobalBuiltinRole,
    ArkDPADBSqlServerDatabaseBuiltinRole,
    ArkDPADBSqlServerGlobalBuiltinRole,
)


class ArkDPADBResourceIdentifierType(str, Enum):
    RESOURCE = 'resource'
    TAG = 'tag'


class ArkDPADBAppliedTo(ArkCamelizedModel):
    name: str = Field(description='Name of the resource to apply the auth to')
    type: ArkDPADBResourceIdentifierType = Field(description='Type of the resource')


class ArkDPADBBaseAuth(ArkCamelizedModel):
    applied_to: Optional[List[ArkDPADBAppliedTo]] = Field(description='Which resources to apply to')


class ArkDPADBLDAPAuth(ArkDPADBBaseAuth):
    assign_groups: List[str] = Field(description='LDAP groups to assign the ephemeral user to')


class ArkDPADBLocalDBAuth(ArkDPADBBaseAuth):
    roles: List[str] = Field(description='Local DB roles to assign the ephemeral user to')


class ArkDPADBOracleDBAuth(ArkDPADBBaseAuth):
    roles: List[str] = Field(description='Local DB roles to assign the ephemeral user to')
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


class ArkDPADBRDSIAMUserAuth(ArkDPADBBaseAuth):
    db_user: str = Field(description='The RDS DB User to use for the connection')


class ArkDPADBSqlServerAuth(ArkDPADBBaseAuth):
    global_builtin_roles: List[ArkDPADBSqlServerGlobalBuiltinRole] = Field(description='Global MSSQL built in roles', default_factory=list)
    global_custom_roles: List[str] = Field(description='Global MSSQL custom roles', default_factory=list)
    database_builtin_roles: Dict[str, List[ArkDPADBSqlServerDatabaseBuiltinRole]] = Field(
        description='Per database builtin roles', default_factory=dict
    )
    database_custom_roles: Dict[str, List[str]] = Field(alias='Custom per database roles', default_factory=dict)


class ArkDPADBConnectAs(ArkCamelizedModel):
    ldap_auth: Optional[List[ArkDPADBLDAPAuth]] = Field(description='LDAP related authentication, only applies to MSSQL DB')
    db_auth: Optional[List[ArkDPADBLocalDBAuth]] = Field(
        description='Local DB related authentication, only applies to MySQL / MariaDB / Postgres'
    )
    oracle_auth: Optional[List[ArkDPADBOracleDBAuth]] = Field(description='Oracle DB related authentication, only applies to Oracle')
    mongo_auth: Optional[List[ArkDPADBMongoDBAuth]] = Field(description='Mongo DB related authentication, only applies to Mongo')
    sqlserver_auth: Optional[List[ArkDPADBSqlServerAuth]] = Field(
        description='SQL Server DB related authentication, only applies to SQL Server using local auth'
    )
    rds_iam_user_auth: Optional[List[ArkDPADBRDSIAMUserAuth]] = Field(
        description='RDS IAM Related Authentication, only applies to RDS related DBs who support IAM Auth'
    )
