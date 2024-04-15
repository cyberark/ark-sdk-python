# pylint: disable=invalid-name
from enum import Enum
from typing import Dict, Final, List, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel
from ark_sdk_python.models.common.ark_workspace_type import ArkWorkspaceType
from ark_sdk_python.models.services.dpa.workspaces.db.ark_dpa_db_provider import ArkDPADBDatabaseFamilyType


class ArkDPADBAuthMethodType(str, Enum):
    ADEphemeralUser = 'ad_ephemeral_user'
    LocalEphemeralUser = 'local_ephemeral_user'
    RDSIAMAuthentication = 'rds_iam_authentication'


class ArkDPADBAuthMethod(ArkCamelizedModel):
    id: int = Field(description='ID of the authentication method on the database')
    auth_method_type: ArkDPADBAuthMethodType = Field(description='Type / name of the authentication method')
    description: str = Field(description='Description about the authentication method')
    workspaces: List[ArkWorkspaceType] = Field(description='Workspaces this authentication method is used in')


class ArkDPADBDatabaseAuthMethod(ArkCamelizedModel):
    id: int = Field(description='ID of the relation between the authentication method and the database type')
    provider_family: ArkDPADBDatabaseFamilyType = Field(description='Name of the database family this authentication method is used for')
    auth_method: ArkDPADBAuthMethod = Field(description='The actual authentication method')
    method_enabled: bool = Field(description='Whether this authentication method is enabled or not')


class ArkDPADBDatabaseTargetConfiguredAuthMethod(ArkCamelizedModel):
    database_auth_method: ArkDPADBDatabaseAuthMethod = Field(description='Identifier for the configured auth method')
    database_target_id: int = Field(description='Database target identifier')
    configured_auth_method_id: Optional[int] = Field(description='The configured auth method id for the target')


DATABASES_FAMILIES_TO_DEFAULT_AUTH_METHOD: Final[Dict[ArkDPADBDatabaseFamilyType, ArkDPADBAuthMethodType]] = {
    ArkDPADBDatabaseFamilyType.Postgres: ArkDPADBAuthMethodType.LocalEphemeralUser,
    ArkDPADBDatabaseFamilyType.Oracle: ArkDPADBAuthMethodType.LocalEphemeralUser,
    ArkDPADBDatabaseFamilyType.MSSQL: ArkDPADBAuthMethodType.ADEphemeralUser,
    ArkDPADBDatabaseFamilyType.MySQL: ArkDPADBAuthMethodType.LocalEphemeralUser,
    ArkDPADBDatabaseFamilyType.MariaDB: ArkDPADBAuthMethodType.LocalEphemeralUser,
    ArkDPADBDatabaseFamilyType.DB2: ArkDPADBAuthMethodType.ADEphemeralUser,
    ArkDPADBDatabaseFamilyType.Mongo: ArkDPADBAuthMethodType.LocalEphemeralUser,
}
