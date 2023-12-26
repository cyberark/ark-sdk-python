from pydantic import Field

from ark_sdk_python.models.services.dpa.db.ark_dpa_db_base_execution import ArkDPADBBaseExecution


class ArkDPADBMysqlExecution(ArkDPADBBaseExecution):
    mysql_path: str = Field(description='Path to the psql executable', default='mysql')
