from ark_sdk_python.models import ArkException
from ark_sdk_python.models.common import ArkWorkspaceType


def serialize_dpa_vm_policies_workspace_type(ws_type: ArkWorkspaceType) -> str:
    if isinstance(ws_type, str):
        ws_type = ArkWorkspaceType(ws_type)
    if ws_type == ArkWorkspaceType.AWS:
        return 'AWS'
    elif ws_type == ArkWorkspaceType.AZURE:
        return 'Azure'
    elif ws_type == ArkWorkspaceType.GCP:
        return 'GCP'
    elif ws_type == ArkWorkspaceType.ONPREM:
        return 'OnPrem'
    raise ArkException('Invalid VM Policies Workspace Type')
