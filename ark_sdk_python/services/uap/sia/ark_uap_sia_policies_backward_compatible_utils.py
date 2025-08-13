"""
Utilities for backward compatibility and migration from old SIA policies management to UAP SIA policies management.

This module provides helper mappings and functions to assist customers in converting their SIA policy management scripts.
The file contains definitions and types to the new Unified Access Policies (UAP) model.
"""

from typing import Dict, Final, Tuple

from ark_sdk_python.models.services.sia.workspaces.db import ArkSIADBAuthMethodType, ArkSIADBDatabaseFamilyType
from ark_sdk_python.models.services.uap.sia.db import ArkUAPSIADBAuthenticationMethod

ARK_UAP_SIA_DB_AUTH_METHOD_FAMILY_TO_DB_AUTH_METHOD: Final[
    Dict[Tuple[ArkSIADBAuthMethodType, ArkSIADBDatabaseFamilyType], ArkUAPSIADBAuthenticationMethod]
] = {
    (ArkSIADBAuthMethodType.ADEphemeralUser, ArkSIADBDatabaseFamilyType.MSSQL): ArkUAPSIADBAuthenticationMethod.LDAP_AUTH,
    (ArkSIADBAuthMethodType.ADEphemeralUser, ArkSIADBDatabaseFamilyType.DB2): ArkUAPSIADBAuthenticationMethod.LDAP_AUTH,
    (ArkSIADBAuthMethodType.LocalEphemeralUser, ArkSIADBDatabaseFamilyType.MySQL): ArkUAPSIADBAuthenticationMethod.DB_AUTH,
    (ArkSIADBAuthMethodType.LocalEphemeralUser, ArkSIADBDatabaseFamilyType.MariaDB): ArkUAPSIADBAuthenticationMethod.DB_AUTH,
    (ArkSIADBAuthMethodType.LocalEphemeralUser, ArkSIADBDatabaseFamilyType.Postgres): ArkUAPSIADBAuthenticationMethod.DB_AUTH,
    (ArkSIADBAuthMethodType.RDSIAMAuthentication, ArkSIADBDatabaseFamilyType.MySQL): ArkUAPSIADBAuthenticationMethod.RDS_IAM_USER_AUTH,
    (ArkSIADBAuthMethodType.RDSIAMAuthentication, ArkSIADBDatabaseFamilyType.MariaDB): ArkUAPSIADBAuthenticationMethod.RDS_IAM_USER_AUTH,
    (ArkSIADBAuthMethodType.RDSIAMAuthentication, ArkSIADBDatabaseFamilyType.Postgres): ArkUAPSIADBAuthenticationMethod.RDS_IAM_USER_AUTH,
    (ArkSIADBAuthMethodType.AtlasEphemeralUser, ArkSIADBDatabaseFamilyType.Mongo): ArkUAPSIADBAuthenticationMethod.MONGO_AUTH,
    (ArkSIADBAuthMethodType.LocalEphemeralUser, ArkSIADBDatabaseFamilyType.Mongo): ArkUAPSIADBAuthenticationMethod.MONGO_AUTH,
    (ArkSIADBAuthMethodType.LocalEphemeralUser, ArkSIADBDatabaseFamilyType.MSSQL): ArkUAPSIADBAuthenticationMethod.SQLSERVER_AUTH,
    (ArkSIADBAuthMethodType.LocalEphemeralUser, ArkSIADBDatabaseFamilyType.Oracle): ArkUAPSIADBAuthenticationMethod.ORACLE_AUTH,
}
