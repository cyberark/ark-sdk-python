# pylint: disable=invalid-name
from enum import Enum


class ArkSIADBMongoGlobalBuiltinRole(str, Enum):
    Root = 'root'
    DbAdminAnyDatabase = 'dbAdminAnyDatabase'
    UserAdminAnyDatabase = 'userAdminAnyDatabase'
    ReadWriteAnyDatabase = 'readWriteAnyDatabase'
    ReadAnyDatabase = 'readAnyDatabase'
    Backup = 'backup'
    Restore = 'restore'
    ClusterAdmin = 'clusterAdmin'
    ClusterManager = 'clusterManager'
    ClusterMonitor = 'clusterMonitor'
    HostManager = 'hostManager'


class ArkSIADBMongoDatabaseBuiltinRole(str, Enum):
    UserAdmin = 'userAdmin'
    DbOwner = 'dbOwner'
    DbAdmin = 'dbAdmin'
    ReadWrite = 'readWrite'
    Read = 'read'


class ArkSIADBSqlServerGlobalBuiltinRole(str, Enum):
    SysAdmin = 'sysadmin'
    ServerAdmin = 'serveradmin'
    SecurityAdmin = 'securityadmin'
    ProcessAdmin = 'processadmin'
    SetupAdmin = 'setupadmin'
    BulkAdmin = 'bulkadmin'
    DiskAdmin = 'diskadmin'
    DbCreator = 'dbcreator'


class ArkSIADBSqlServerDatabaseBuiltinRole(str, Enum):
    DbOwner = 'db_owner'
    DbSecurityAdmin = 'db_securityadmin'
    DbAccessAdmin = 'db_accessadmin'
    DbBackupOperator = 'db_backupoperator'
    DbDdlAdmin = 'db_ddladmin'
    DbDataWriter = 'db_datawriter'
    DbDataReader = 'db_datareader'
    DbDenyDataWriter = 'db_denydatawriter'
    DbDenyDataReader = 'db_denydatareader'
