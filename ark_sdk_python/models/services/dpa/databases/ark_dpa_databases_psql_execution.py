from pydantic import Field

from ark_sdk_python.models.services.dpa.databases.ark_dpa_databases_base_execution import ArkDPADatabasesBaseExecution


class ArkDPADatabasesPsqlExecution(ArkDPADatabasesBaseExecution):
    psql_path: str = Field(description='Path to the psql executable', default='psql')
