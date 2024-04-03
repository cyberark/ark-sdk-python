# pylint: disable=invalid-name
from enum import Enum
from typing import Dict, Final

from pydantic import BaseModel, Field


class ArkDPADBDatabaseEngineType(str, Enum):
    AuroraPostgres = 'aurora-postgresql'
    AuroraMysql = 'aurora-mysql'
    CustomSqlServerEE = 'custom-sqlserver-ee'
    CustomSqlServerSE = 'custom-sqlserver-se'
    CustomSqlServerWeb = 'custom-sqlserver-web'
    OracleEE = 'oracle-ee'
    OracleEECDB = 'oracle-ee-cdb'
    OracleSE2 = 'oracle-se2'
    OracleSE2CDB = 'oracle-se2-cdb'
    SqlServer = 'sqlserver'
    Oracle = 'oracle'
    MSSQL = 'mssql'
    MariaDB = 'mariadb'
    MySQL = 'mysql'
    Postgres = 'postgres'
    SqlServerSH = 'sqlserver-sh'
    MSSQLSH = 'mssql-sh'
    MySQLSH = 'mysql-sh'
    MariaDBSH = 'mariadb-sh'
    PostgresSH = 'postgres-sh'
    OracleSH = 'oracle-sh'
    DB2 = 'db2'
    DB2SH = 'db2-sh'
    Mongo = 'mongo'
    MongoSH = 'mongo-sh'


class ArkDPADBDatabaseFamilyType(str, Enum):
    Postgres = 'Postgres'
    Oracle = 'Oracle'
    MSSQL = 'MSSQL'
    MySQL = 'MySQL'
    MariaDB = 'MariaDB'
    DB2 = 'DB2'
    Mongo = 'Mongo'
    Unknown = 'Unknown'


class ArkDPADBDatabaseWorkspaceType(str, Enum):
    Cloud = 'cloud'
    SelfHosted = 'self-hosted'


class ArkDPADBDatabaseProvider(BaseModel):
    id: int = Field(description='ID of the provider')
    engine: ArkDPADBDatabaseEngineType = Field(description='Engine type of the database provider')
    workspace: ArkDPADBDatabaseWorkspaceType = Field(description='Workspace of the database provider')
    family: ArkDPADBDatabaseFamilyType = Field(description='Family of the database provider')


DATABASES_ENGINES_TO_FAMILY: Final[Dict[ArkDPADBDatabaseEngineType, ArkDPADBDatabaseFamilyType]] = {
    ArkDPADBDatabaseEngineType.AuroraMysql: ArkDPADBDatabaseFamilyType.MySQL,
    ArkDPADBDatabaseEngineType.AuroraPostgres: ArkDPADBDatabaseFamilyType.Postgres,
    ArkDPADBDatabaseEngineType.CustomSqlServerEE: ArkDPADBDatabaseFamilyType.MSSQL,
    ArkDPADBDatabaseEngineType.CustomSqlServerSE: ArkDPADBDatabaseFamilyType.MSSQL,
    ArkDPADBDatabaseEngineType.CustomSqlServerWeb: ArkDPADBDatabaseFamilyType.MSSQL,
    ArkDPADBDatabaseEngineType.MariaDB: ArkDPADBDatabaseFamilyType.MariaDB,
    ArkDPADBDatabaseEngineType.MariaDBSH: ArkDPADBDatabaseFamilyType.MariaDB,
    ArkDPADBDatabaseEngineType.MSSQL: ArkDPADBDatabaseFamilyType.MSSQL,
    ArkDPADBDatabaseEngineType.MSSQLSH: ArkDPADBDatabaseFamilyType.MSSQL,
    ArkDPADBDatabaseEngineType.MySQL: ArkDPADBDatabaseFamilyType.MySQL,
    ArkDPADBDatabaseEngineType.MySQLSH: ArkDPADBDatabaseFamilyType.MySQL,
    ArkDPADBDatabaseEngineType.Oracle: ArkDPADBDatabaseFamilyType.Oracle,
    ArkDPADBDatabaseEngineType.OracleEE: ArkDPADBDatabaseFamilyType.Oracle,
    ArkDPADBDatabaseEngineType.OracleSH: ArkDPADBDatabaseFamilyType.Oracle,
    ArkDPADBDatabaseEngineType.OracleEECDB: ArkDPADBDatabaseFamilyType.Oracle,
    ArkDPADBDatabaseEngineType.OracleSE2CDB: ArkDPADBDatabaseFamilyType.Oracle,
    ArkDPADBDatabaseEngineType.OracleSE2: ArkDPADBDatabaseFamilyType.Oracle,
    ArkDPADBDatabaseEngineType.Postgres: ArkDPADBDatabaseFamilyType.Postgres,
    ArkDPADBDatabaseEngineType.PostgresSH: ArkDPADBDatabaseFamilyType.Postgres,
    ArkDPADBDatabaseEngineType.SqlServer: ArkDPADBDatabaseFamilyType.MSSQL,
    ArkDPADBDatabaseEngineType.SqlServerSH: ArkDPADBDatabaseFamilyType.MSSQL,
    ArkDPADBDatabaseEngineType.DB2: ArkDPADBDatabaseFamilyType.DB2,
    ArkDPADBDatabaseEngineType.DB2SH: ArkDPADBDatabaseFamilyType.DB2,
    ArkDPADBDatabaseEngineType.Mongo: ArkDPADBDatabaseFamilyType.Mongo,
    ArkDPADBDatabaseEngineType.MongoSH: ArkDPADBDatabaseFamilyType.Mongo,
}


DATABASE_FAMILIES_DEFAULT_PORTS: Final[Dict[ArkDPADBDatabaseFamilyType, int]] = {
    ArkDPADBDatabaseFamilyType.Postgres: 5432,
    ArkDPADBDatabaseFamilyType.Oracle: 2484,
    ArkDPADBDatabaseFamilyType.MSSQL: 1433,
    ArkDPADBDatabaseFamilyType.MySQL: 3306,
    ArkDPADBDatabaseFamilyType.MariaDB: 3306,
    ArkDPADBDatabaseFamilyType.DB2: 50002,
    ArkDPADBDatabaseFamilyType.Mongo: 27017,
}
