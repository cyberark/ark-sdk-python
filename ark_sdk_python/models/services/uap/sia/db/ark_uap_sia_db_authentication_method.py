from enum import Enum


class ArkUAPSIADBAuthenticationMethod(str, Enum):
    LDAP_AUTH = 'ldap_auth'
    DB_AUTH = 'db_auth'
    ORACLE_AUTH = 'oracle_auth'
    MONGO_AUTH = 'mongo_auth'
    SQLSERVER_AUTH = 'sqlserver_auth'
    RDS_IAM_USER_AUTH = 'rds_iam_user_auth'
