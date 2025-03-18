# pylint: disable=invalid-name
from enum import Enum
from typing import Dict, Final

from pydantic import BaseModel, Field


class ArkSIADBDatabaseEngineType(str, Enum):
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
    MSSQLSHVM = 'mssql-sh-vm'
    MSSQLAzureManaged = 'mssql-azure-managed'
    MSSQLAzureVM = 'mssql-azure-vm'
    MSSQLAWSEC2 = 'mssql-aws-ec2'
    MSSQLAWSRDS = 'mssql-aws-rds'
    DB2AWSRDS = 'db2-aws-rds'
    DB2SHVM = 'db2-sh-vm'
    OracleAWSRDS = 'oracle-aws-rds'
    OracleAWSVM = 'oracle-aws-vm'
    OracleSHVM = 'oracle-sh-vm'
    MariaDBSHVM = 'mariadb-sh-vm'
    MariaDBAzureManaged = 'mariadb-azure-managed'
    MariaDBAzureVM = 'mariadb-azure-vm'
    MariaDBAWSVM = 'mariadb-aws-vm'
    MariaDBAWSRDS = 'mariadb-aws-rds'
    MariaDBAWSAurora = 'mariadb-aws-aurora'
    MySQLSHVM = 'mysql-sh-vm'
    MySQLAzureManaged = 'mysql-azure-managed'
    MySQLAzureVM = 'mysql-azure-vm'
    MySQLAWSVM = 'mysql-aws-vm'
    MySQLAWSRDS = 'mysql-aws-rds'
    MySQLAWSAurora = 'mysql-aws-aurora'
    PostgresSHVM = 'postgres-sh-vm'
    PostgresAzureManaged = 'postgres-azure-managed'
    PostgresAzureVM = 'postgres-azure-vm'
    PostgresAWSVM = 'postgres-aws-vm'
    PostgresAWSRDS = 'postgres-aws-rds'
    PostgresAWSAurora = 'postgres-aws-aurora'
    MongoSHVM = 'mongo-sh-vm'
    MongoAWSDocDB = 'mongo-aws-docdb'
    MongoAtlasManaged = 'mongo-atlas-managed'


class ArkSIADBDatabaseFamilyType(str, Enum):
    Postgres = 'Postgres'
    Oracle = 'Oracle'
    MSSQL = 'MSSQL'
    MySQL = 'MySQL'
    MariaDB = 'MariaDB'
    DB2 = 'DB2'
    Mongo = 'Mongo'
    Unknown = 'Unknown'


class ArkSIADBDatabaseWorkspaceType(str, Enum):
    Cloud = 'cloud'
    SelfHosted = 'self-hosted'


class ArkSIADBDatabaseProvider(BaseModel):
    id: int = Field(description='ID of the provider')
    engine: ArkSIADBDatabaseEngineType = Field(description='Engine type of the database provider')
    workspace: ArkSIADBDatabaseWorkspaceType = Field(description='Workspace of the database provider')
    family: ArkSIADBDatabaseFamilyType = Field(description='Family of the database provider')


DATABASES_ENGINES_TO_FAMILY: Final[Dict[ArkSIADBDatabaseEngineType, ArkSIADBDatabaseFamilyType]] = {
    ArkSIADBDatabaseEngineType.AuroraMysql: ArkSIADBDatabaseFamilyType.MySQL,
    ArkSIADBDatabaseEngineType.AuroraPostgres: ArkSIADBDatabaseFamilyType.Postgres,
    ArkSIADBDatabaseEngineType.CustomSqlServerEE: ArkSIADBDatabaseFamilyType.MSSQL,
    ArkSIADBDatabaseEngineType.CustomSqlServerSE: ArkSIADBDatabaseFamilyType.MSSQL,
    ArkSIADBDatabaseEngineType.CustomSqlServerWeb: ArkSIADBDatabaseFamilyType.MSSQL,
    ArkSIADBDatabaseEngineType.MariaDB: ArkSIADBDatabaseFamilyType.MariaDB,
    ArkSIADBDatabaseEngineType.MariaDBSH: ArkSIADBDatabaseFamilyType.MariaDB,
    ArkSIADBDatabaseEngineType.MSSQL: ArkSIADBDatabaseFamilyType.MSSQL,
    ArkSIADBDatabaseEngineType.MSSQLSH: ArkSIADBDatabaseFamilyType.MSSQL,
    ArkSIADBDatabaseEngineType.MySQL: ArkSIADBDatabaseFamilyType.MySQL,
    ArkSIADBDatabaseEngineType.MySQLSH: ArkSIADBDatabaseFamilyType.MySQL,
    ArkSIADBDatabaseEngineType.Oracle: ArkSIADBDatabaseFamilyType.Oracle,
    ArkSIADBDatabaseEngineType.OracleEE: ArkSIADBDatabaseFamilyType.Oracle,
    ArkSIADBDatabaseEngineType.OracleSH: ArkSIADBDatabaseFamilyType.Oracle,
    ArkSIADBDatabaseEngineType.OracleEECDB: ArkSIADBDatabaseFamilyType.Oracle,
    ArkSIADBDatabaseEngineType.OracleSE2CDB: ArkSIADBDatabaseFamilyType.Oracle,
    ArkSIADBDatabaseEngineType.OracleSE2: ArkSIADBDatabaseFamilyType.Oracle,
    ArkSIADBDatabaseEngineType.Postgres: ArkSIADBDatabaseFamilyType.Postgres,
    ArkSIADBDatabaseEngineType.PostgresSH: ArkSIADBDatabaseFamilyType.Postgres,
    ArkSIADBDatabaseEngineType.SqlServer: ArkSIADBDatabaseFamilyType.MSSQL,
    ArkSIADBDatabaseEngineType.SqlServerSH: ArkSIADBDatabaseFamilyType.MSSQL,
    ArkSIADBDatabaseEngineType.DB2: ArkSIADBDatabaseFamilyType.DB2,
    ArkSIADBDatabaseEngineType.DB2SH: ArkSIADBDatabaseFamilyType.DB2,
    ArkSIADBDatabaseEngineType.Mongo: ArkSIADBDatabaseFamilyType.Mongo,
    ArkSIADBDatabaseEngineType.MongoSH: ArkSIADBDatabaseFamilyType.Mongo,
    ArkSIADBDatabaseEngineType.MSSQLSHVM: ArkSIADBDatabaseFamilyType.MSSQL,
    ArkSIADBDatabaseEngineType.MSSQLAzureManaged: ArkSIADBDatabaseFamilyType.MSSQL,
    ArkSIADBDatabaseEngineType.MSSQLAzureVM: ArkSIADBDatabaseFamilyType.MSSQL,
    ArkSIADBDatabaseEngineType.MSSQLAWSEC2: ArkSIADBDatabaseFamilyType.MSSQL,
    ArkSIADBDatabaseEngineType.MSSQLAWSRDS: ArkSIADBDatabaseFamilyType.MSSQL,
    ArkSIADBDatabaseEngineType.DB2AWSRDS: ArkSIADBDatabaseFamilyType.DB2,
    ArkSIADBDatabaseEngineType.DB2SHVM: ArkSIADBDatabaseFamilyType.DB2,
    ArkSIADBDatabaseEngineType.OracleAWSRDS: ArkSIADBDatabaseFamilyType.Oracle,
    ArkSIADBDatabaseEngineType.OracleAWSVM: ArkSIADBDatabaseFamilyType.Oracle,
    ArkSIADBDatabaseEngineType.OracleSHVM: ArkSIADBDatabaseFamilyType.Oracle,
    ArkSIADBDatabaseEngineType.MariaDBSHVM: ArkSIADBDatabaseFamilyType.MariaDB,
    ArkSIADBDatabaseEngineType.MariaDBAzureManaged: ArkSIADBDatabaseFamilyType.MariaDB,
    ArkSIADBDatabaseEngineType.MariaDBAzureVM: ArkSIADBDatabaseFamilyType.MariaDB,
    ArkSIADBDatabaseEngineType.MariaDBAWSVM: ArkSIADBDatabaseFamilyType.MariaDB,
    ArkSIADBDatabaseEngineType.MariaDBAWSRDS: ArkSIADBDatabaseFamilyType.MariaDB,
    ArkSIADBDatabaseEngineType.MariaDBAWSAurora: ArkSIADBDatabaseFamilyType.MariaDB,
    ArkSIADBDatabaseEngineType.MySQLSHVM: ArkSIADBDatabaseFamilyType.MySQL,
    ArkSIADBDatabaseEngineType.MySQLAzureManaged: ArkSIADBDatabaseFamilyType.MySQL,
    ArkSIADBDatabaseEngineType.MySQLAzureVM: ArkSIADBDatabaseFamilyType.MySQL,
    ArkSIADBDatabaseEngineType.MySQLAWSVM: ArkSIADBDatabaseFamilyType.MySQL,
    ArkSIADBDatabaseEngineType.MySQLAWSRDS: ArkSIADBDatabaseFamilyType.MySQL,
    ArkSIADBDatabaseEngineType.MySQLAWSAurora: ArkSIADBDatabaseFamilyType.MySQL,
    ArkSIADBDatabaseEngineType.PostgresSHVM: ArkSIADBDatabaseFamilyType.Postgres,
    ArkSIADBDatabaseEngineType.PostgresAzureManaged: ArkSIADBDatabaseFamilyType.Postgres,
    ArkSIADBDatabaseEngineType.PostgresAzureVM: ArkSIADBDatabaseFamilyType.Postgres,
    ArkSIADBDatabaseEngineType.PostgresAWSVM: ArkSIADBDatabaseFamilyType.Postgres,
    ArkSIADBDatabaseEngineType.PostgresAWSRDS: ArkSIADBDatabaseFamilyType.Postgres,
    ArkSIADBDatabaseEngineType.PostgresAWSAurora: ArkSIADBDatabaseFamilyType.Postgres,
    ArkSIADBDatabaseEngineType.MongoSHVM: ArkSIADBDatabaseFamilyType.Mongo,
    ArkSIADBDatabaseEngineType.MongoAWSDocDB: ArkSIADBDatabaseFamilyType.Mongo,
    ArkSIADBDatabaseEngineType.MongoAtlasManaged: ArkSIADBDatabaseFamilyType.Mongo,
}


DATABASE_FAMILIES_DEFAULT_PORTS: Final[Dict[ArkSIADBDatabaseFamilyType, int]] = {
    ArkSIADBDatabaseFamilyType.Postgres: 5432,
    ArkSIADBDatabaseFamilyType.Oracle: 2484,
    ArkSIADBDatabaseFamilyType.MSSQL: 1433,
    ArkSIADBDatabaseFamilyType.MySQL: 3306,
    ArkSIADBDatabaseFamilyType.MariaDB: 3306,
    ArkSIADBDatabaseFamilyType.DB2: 50002,
    ArkSIADBDatabaseFamilyType.Mongo: 27017,
}
