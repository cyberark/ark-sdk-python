from ark_sdk_python.models import ArkException
from ark_sdk_python.models.common import ArkWorkspaceType


def serialize_db_platform_type(ws_type: ArkWorkspaceType):
    if isinstance(ws_type, str):
        ws_type = ArkWorkspaceType(ws_type)
    if ws_type == ArkWorkspaceType.AWS:
        return 'AWS'
    elif ws_type == ArkWorkspaceType.AZURE:
        return 'AZURE'
    elif ws_type == ArkWorkspaceType.GCP:
        return 'GCP'
    elif ws_type == ArkWorkspaceType.ONPREM:
        return 'ON-PREMISE'
    raise ArkException('Invalid DB Platform Type')
