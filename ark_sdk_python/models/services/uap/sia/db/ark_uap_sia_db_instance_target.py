from typing import Any, Dict, Optional

from pydantic import Field, model_validator
from typing_extensions import Annotated

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.sia.workspaces.db import ArkSIADBDatabaseFamilyType
from ark_sdk_python.models.services.uap.sia.db.ark_uap_sia_db_authentication_method import ArkUAPSIADBAuthenticationMethod
from ark_sdk_python.models.services.uap.sia.db.ark_uap_sia_db_consts import UAP_SIA_DB_INSTANCE_ID_LENGTH, UAP_SIA_DB_INSTANCE_NAME_LENGTH
from ark_sdk_python.models.services.uap.sia.db.ark_uap_sia_db_profiles import (
    ArkUAPSIADBLDAPAuthProfile,
    ArkUAPSIADBLocalDBAuthProfile,
    ArkUAPSIADBMongoAuthProfile,
    ArkUAPSIADBOracleDBAuthProfile,
    ArkUAPSIADBProfile,
    ArkUAPSIADBRDSIAMUserAuthProfile,
    ArkUAPSIADBSqlServerAuthProfile,
)


class ArkUAPSIADBInstanceTarget(ArkCamelizedModel):
    instance_name: Annotated[
        str, Field(strict=True, min_length=1, max_length=UAP_SIA_DB_INSTANCE_NAME_LENGTH, description='The name of the database instance')
    ]
    instance_type: Annotated[ArkSIADBDatabaseFamilyType, Field(description='The database type of the database instance')]
    instance_id: Annotated[
        str, Field(strict=True, min_length=1, max_length=UAP_SIA_DB_INSTANCE_ID_LENGTH, description='The id of the database instance')
    ]
    authentication_method: Annotated[
        ArkUAPSIADBAuthenticationMethod, Field(description='The authentication method corresponding to this profile')
    ]

    # Profiles, only one of these will be set based on the authentication method.
    # Note that the API has a single profiles field, but we separate them here for clarity and easier usage.
    ldap_auth_profile: Annotated[
        Optional[ArkUAPSIADBLDAPAuthProfile], Field(description='The LDAP authentication profile for this database instance')
    ] = None
    db_auth_profile: Annotated[
        Optional[ArkUAPSIADBLocalDBAuthProfile],
        Field(description='The local database authentication profile for this database instance'),
    ] = None
    oracle_db_auth_profile: Annotated[
        ArkUAPSIADBOracleDBAuthProfile,
        Field(description='The Oracle database authentication profile for this database instance'),
    ] = None
    mongo_auth_profile: Annotated[
        Optional[ArkUAPSIADBMongoAuthProfile],
        Field(description='The MongoDB authentication profile for this database instance'),
    ] = None
    sql_server_auth_profile: Annotated[
        Optional[ArkUAPSIADBSqlServerAuthProfile],
        Field(description='The SQL Server authentication profile for this database instance'),
    ] = None
    rds_iam_user_auth_profile: Annotated[
        Optional[ArkUAPSIADBRDSIAMUserAuthProfile],
        Field(description='The RDS IAM User authentication profile for this database instance'),
    ] = None

    def databases_count(self) -> int:
        profile = self.profile_by_authentication_method()

        if not profile:
            raise ValueError(
                f'No profile found for the given authentication method, instance: [{self.instance_name}], authentication method: [{self.authentication_method}]'
            )

        return profile.databases_count()

    def profile_by_authentication_method(self) -> ArkUAPSIADBProfile:
        """
        Returns the profile corresponding to the authentication method.
        """
        if self.authentication_method == ArkUAPSIADBAuthenticationMethod.LDAP_AUTH:
            return self.ldap_auth_profile
        if self.authentication_method == ArkUAPSIADBAuthenticationMethod.DB_AUTH:
            return self.db_auth_profile
        if self.authentication_method == ArkUAPSIADBAuthenticationMethod.ORACLE_AUTH:
            return self.oracle_db_auth_profile
        if self.authentication_method == ArkUAPSIADBAuthenticationMethod.MONGO_AUTH:
            return self.mongo_auth_profile
        if self.authentication_method == ArkUAPSIADBAuthenticationMethod.SQLSERVER_AUTH:
            return self.sql_server_auth_profile
        if self.authentication_method == ArkUAPSIADBAuthenticationMethod.RDS_IAM_USER_AUTH:
            return self.rds_iam_user_auth_profile

        raise ValueError(f'Unsupported authentication method: {self.authentication_method}')

    @model_validator(mode='before')
    @classmethod
    def move_profile_to_specific_field(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        if 'profile' not in data:
            return data

        auth_method = data.get('authentication_method') or data.get('authenticationMethod')
        if not auth_method:
            return data  # This case will throw an error later since authentication method is defined as required,

        if isinstance(auth_method, str):
            auth_method = ArkUAPSIADBAuthenticationMethod(auth_method)

        profile_field_name = cls.auth_method_to_profile_field_name().get(auth_method)
        if not profile_field_name:
            raise ValueError(f'Unsupported authentication method for profile: {auth_method}')

        # Move 'profile' to the specific field.
        data[profile_field_name] = data.pop('profile')
        return data

    @classmethod
    def auth_method_to_profile_field_name(cls) -> Dict[ArkUAPSIADBAuthenticationMethod, str]:
        return {
            ArkUAPSIADBAuthenticationMethod.LDAP_AUTH: 'ldapAuthProfile',
            ArkUAPSIADBAuthenticationMethod.DB_AUTH: 'dbAuthProfile',
            ArkUAPSIADBAuthenticationMethod.ORACLE_AUTH: 'oracleDbAuthProfile',
            ArkUAPSIADBAuthenticationMethod.MONGO_AUTH: 'mongoAuthProfile',
            ArkUAPSIADBAuthenticationMethod.SQLSERVER_AUTH: 'sqlServerAuthProfile',
            ArkUAPSIADBAuthenticationMethod.RDS_IAM_USER_AUTH: 'rdsIamUserAuthProfile',
        }
