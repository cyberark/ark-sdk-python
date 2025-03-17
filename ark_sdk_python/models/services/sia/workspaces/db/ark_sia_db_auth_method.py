# pylint: disable=invalid-name
from enum import Enum
from typing import Dict, Final, List, Optional

from pydantic import Field, field_validator

from ark_sdk_python.models.ark_model import ArkCamelizedModel
from ark_sdk_python.models.common.ark_workspace_type import ArkWorkspaceType
from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_provider import ArkSIADBDatabaseFamilyType


class ArkSIADBAuthMethodType(str, Enum):
    ADEphemeralUser = 'ad_ephemeral_user'
    LocalEphemeralUser = 'local_ephemeral_user'
    RDSIAMAuthentication = 'rds_iam_authentication'
    AtlasEphemeralUser = 'atlas_ephemeral_user'


class ArkSIADBAuthMethod(ArkCamelizedModel):
    id: int = Field(description='ID of the authentication method on the database')
    auth_method_type: ArkSIADBAuthMethodType = Field(description='Type / name of the authentication method')
    description: str = Field(description='Description about the authentication method')
    workspaces: List[ArkWorkspaceType] = Field(description='Workspaces this authentication method is used in')

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('workspaces', mode="before")
    @classmethod
    def validate_workspace_type(cls, val):
        if val is not None:
            new_vals = []
            for v in val:
                if v and ArkWorkspaceType(v) not in [
                    ArkWorkspaceType.AWS,
                    ArkWorkspaceType.AZURE,
                    ArkWorkspaceType.GCP,
                    ArkWorkspaceType.ONPREM,
                    ArkWorkspaceType.ATLAS,
                ]:
                    raise ValueError('Invalid Platform / Workspace Type')
                new_vals.append(ArkWorkspaceType(v))
            return new_vals
        return val


class ArkSIADBDatabaseAuthMethod(ArkCamelizedModel):
    id: int = Field(description='ID of the relation between the authentication method and the database type')
    provider_family: ArkSIADBDatabaseFamilyType = Field(description='Name of the database family this authentication method is used for')
    auth_method: ArkSIADBAuthMethod = Field(description='The actual authentication method')
    method_enabled: bool = Field(description='Whether this authentication method is enabled or not')


class ArkSIADBDatabaseTargetConfiguredAuthMethod(ArkCamelizedModel):
    database_auth_method: ArkSIADBDatabaseAuthMethod = Field(description='Identifier for the configured auth method')
    database_target_id: int = Field(description='Database target identifier')
    configured_auth_method_id: Optional[int] = Field(default=None, description='The configured auth method id for the target')


DATABASES_FAMILIES_TO_DEFAULT_AUTH_METHOD: Final[Dict[ArkSIADBDatabaseFamilyType, ArkSIADBAuthMethodType]] = {
    ArkSIADBDatabaseFamilyType.Postgres: ArkSIADBAuthMethodType.LocalEphemeralUser,
    ArkSIADBDatabaseFamilyType.Oracle: ArkSIADBAuthMethodType.LocalEphemeralUser,
    ArkSIADBDatabaseFamilyType.MSSQL: ArkSIADBAuthMethodType.ADEphemeralUser,
    ArkSIADBDatabaseFamilyType.MySQL: ArkSIADBAuthMethodType.LocalEphemeralUser,
    ArkSIADBDatabaseFamilyType.MariaDB: ArkSIADBAuthMethodType.LocalEphemeralUser,
    ArkSIADBDatabaseFamilyType.DB2: ArkSIADBAuthMethodType.ADEphemeralUser,
    ArkSIADBDatabaseFamilyType.Mongo: ArkSIADBAuthMethodType.LocalEphemeralUser,
}
