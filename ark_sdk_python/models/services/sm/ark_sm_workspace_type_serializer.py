from ark_sdk_python.models import ArkException
from ark_sdk_python.models.common import ArkWorkspaceType


def serialize_sm_workspace_type(ws_type: ArkWorkspaceType):
    if isinstance(ws_type, str):
        ws_type = ArkWorkspaceType(ws_type)
    if ws_type == ArkWorkspaceType.AWS:
        return 'AWS'
    elif ws_type == ArkWorkspaceType.AZURE:
        return 'Azure'
    elif ws_type == ArkWorkspaceType.ONPREM:
        return 'OnPrem'
    elif ws_type == ArkWorkspaceType.GCP:
        return 'GCP'
    elif ws_type == ArkWorkspaceType.UNKNOWN:
        return 'Unknown'
    raise ArkException('Invalid SM Workspace Type')
