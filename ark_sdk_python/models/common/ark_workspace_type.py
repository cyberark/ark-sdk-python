from aenum import MultiValueEnum


class ArkWorkspaceType(str, MultiValueEnum):
    AWS = 'aws', 'AWS', 'Aws'
    AZURE = 'azure', 'AZURE', 'Azure'
    ONPREM = 'onprem', 'ON-PREMISE', 'OnPrem'
    DB = 'db', 'DATABASES', 'Databases'
    GCP = 'gcp', 'GCP'
    MYSQL = 'mysql', 'MySQL'
    MARIADB = 'mariadb', 'MariaDB'
    MSSQL = 'mssql', 'MSSQL'
    ORACLE = 'oracle', 'Oracle'
    POSTGRES = 'postgres', 'Postgres'
    MONGO = 'mongo', 'Mongo'
    DB2 = 'db2', 'Db2'
    ATLAS = 'atlas', 'ATLAS', 'Atlas'
    FAULT = 'fault', 'FAULT'
    UNKNOWN = 'unknown', 'UNKNOWN', 'Unknown'
    FQDN_IP = 'FQDN/IP', 'fqdn/ip', 'FqdnIp'
