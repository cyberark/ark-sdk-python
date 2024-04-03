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
