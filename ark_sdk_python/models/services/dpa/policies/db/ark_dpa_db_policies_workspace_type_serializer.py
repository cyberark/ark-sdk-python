from ark_sdk_python.models import ArkException
from ark_sdk_python.models.common import ArkWorkspaceType


def serialize_dpa_db_policies_workspace_type(ws_type: ArkWorkspaceType) -> str:
    if isinstance(ws_type, str):
        ws_type = ArkWorkspaceType(ws_type)
    if ws_type == ArkWorkspaceType.MSSQL:
        return 'MSSQL'
    elif ws_type == ArkWorkspaceType.MYSQL:
        return 'MySQL'
    elif ws_type == ArkWorkspaceType.MARIADB:
        return 'MariaDB'
    elif ws_type == ArkWorkspaceType.POSTGRES:
        return 'Postgres'
    elif ws_type == ArkWorkspaceType.ORACLE:
        return 'Oracle'
    elif ws_type == ArkWorkspaceType.MONGO:
        return 'Mongo'
    elif ws_type == ArkWorkspaceType.DB2:
        return 'Db2'
    raise ArkException('Invalid DB Policies Workspace Type')
