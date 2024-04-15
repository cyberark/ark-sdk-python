# pylint: disable=invalid-name
from enum import Enum


class ArkDPADBMongoGlobalBuiltinRole(str, Enum):
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


class ArkDPADBMongoDatabaseBuiltinRole(str, Enum):
    UserAdmin = 'userAdmin'
    DbOwner = 'dbOwner'
    DbAdmin = 'dbAdmin'
    ReadWrite = 'readWrite'
    Read = 'read'


class ArkDPADBSqlServerGlobalBuiltinRole(str, Enum):
    SysAdmin = 'sysadmin'
    ServerAdmin = 'serveradmin'
    SecurityAdmin = 'securityadmin'
    ProcessAdmin = 'processadmin'
    SetupAdmin = 'setupadmin'
    BulkAdmin = 'bulkadmin'
    DiskAdmin = 'diskadmin'
    DbCreator = 'dbcreator'
    Public = 'public'


class ArkDPADBSqlServerDatabaseBuiltinRole(str, Enum):
    DbOwner = 'db_owner'
    DbSecurityAdmin = 'db_securityadmin'
    DbAccessAdmin = 'db_accessadmin'
    DbBackupOperator = 'db_backupoperator'
    DbDdlAdmin = 'db_ddladmin'
    DbDataWriter = 'db_datawriter'
    DbDataReader = 'db_datareader'
    DbDenyDataWriter = 'db_denydatawriter'
    DbDenyDataReader = 'db_denydatareader'
