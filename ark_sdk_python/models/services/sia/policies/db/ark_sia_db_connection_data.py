from enum import Enum
from typing import Dict, List, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel
from ark_sdk_python.models.services.sia.policies.db.ark_sia_db_enums import (
    ArkSIADBMongoDatabaseBuiltinRole,
    ArkSIADBMongoGlobalBuiltinRole,
    ArkSIADBSqlServerDatabaseBuiltinRole,
    ArkSIADBSqlServerGlobalBuiltinRole,
)


class ArkSIADBResourceIdentifierType(str, Enum):
    RESOURCE = 'resource'
    TAG = 'tag'


class ArkSIADBAppliedTo(ArkCamelizedModel):
    name: str = Field(description='Name of the resource to apply the auth to')
    type: ArkSIADBResourceIdentifierType = Field(description='Type of the resource')


class ArkSIADBBaseAuth(ArkCamelizedModel):
    applied_to: Optional[List[ArkSIADBAppliedTo]] = Field(default=None, description='Which resources to apply to')


class ArkSIADBLDAPAuth(ArkSIADBBaseAuth):
    assign_groups: List[str] = Field(description='LDAP groups to assign the ephemeral user to')


class ArkSIADBLocalDBAuth(ArkSIADBBaseAuth):
    roles: List[str] = Field(description='Local DB roles to assign the ephemeral user to')


class ArkSIADBOracleDBAuth(ArkSIADBBaseAuth):
    roles: List[str] = Field(description='Local DB roles to assign the ephemeral user to')
    dba_role: bool = Field(description='Whether to apply to the ephemeral user the DBA role', default=False)
    sysdba_role: bool = Field(description='Whether to apply to the ephemeral user the SYSDBA role', default=False)
    sysoper_role: bool = Field(description='Whether to apply to the ephemeral user the SYSOPER role', default=False)


class ArkSIADBMongoDBAuth(ArkSIADBBaseAuth):
    global_builtin_roles: List[ArkSIADBMongoGlobalBuiltinRole] = Field(
        description='Global builtin roles across all databases', default_factory=list
    )
    database_builtin_roles: Dict[str, List[ArkSIADBMongoDatabaseBuiltinRole]] = Field(
        description='Per database builtin roles', default_factory=dict
    )
    database_custom_roles: Dict[str, List[str]] = Field(description='Custom per database roles', default_factory=dict)


class ArkSIADBRDSIAMUserAuth(ArkSIADBBaseAuth):
    db_user: str = Field(description='The RDS DB User to use for the connection')


class ArkSIADBSqlServerAuth(ArkSIADBBaseAuth):
    global_builtin_roles: List[ArkSIADBSqlServerGlobalBuiltinRole] = Field(description='Global MSSQL built in roles', default_factory=list)
    global_custom_roles: List[str] = Field(description='Global MSSQL custom roles', default_factory=list)
    database_builtin_roles: Dict[str, List[ArkSIADBSqlServerDatabaseBuiltinRole]] = Field(
        description='Per database builtin roles', default_factory=dict
    )
    database_custom_roles: Dict[str, List[str]] = Field(alias='Custom per database roles', default_factory=dict)


class ArkSIADBConnectAs(ArkCamelizedModel):
    ldap_auth: Optional[List[ArkSIADBLDAPAuth]] = Field(default=None, description='LDAP related authentication, only applies to MSSQL DB')
    db_auth: Optional[List[ArkSIADBLocalDBAuth]] = Field(
        default=None, description='Local DB related authentication, only applies to MySQL / MariaDB / Postgres'
    )
    oracle_auth: Optional[List[ArkSIADBOracleDBAuth]] = Field(
        default=None, description='Oracle DB related authentication, only applies to Oracle'
    )
    mongo_auth: Optional[List[ArkSIADBMongoDBAuth]] = Field(
        default=None, description='Mongo DB related authentication, only applies to Mongo'
    )
    sqlserver_auth: Optional[List[ArkSIADBSqlServerAuth]] = Field(
        default=None, description='SQL Server DB related authentication, only applies to SQL Server using local auth'
    )
    rds_iam_user_auth: Optional[List[ArkSIADBRDSIAMUserAuth]] = Field(
        default=None, description='RDS IAM Related Authentication, only applies to RDS related DBs who support IAM Auth'
    )
