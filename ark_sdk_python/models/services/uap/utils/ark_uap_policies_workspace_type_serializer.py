from typing import List

from ark_sdk_python.models import ArkException
from ark_sdk_python.models.common import ArkWorkspaceType


def serialize_uap_policies_workspace_type(ws_type: ArkWorkspaceType) -> str:
    if ws_type == ArkWorkspaceType.AWS:
        return 'AWS'
    elif ws_type == ArkWorkspaceType.AZURE:
        return 'Azure'
    elif ws_type == ArkWorkspaceType.GCP:
        return 'GCP'
    elif ws_type == ArkWorkspaceType.FQDN_IP:
        return 'FQDN/IP'
    raise ArkException('Invalid Policies Workspace Type')


def serialize_uap_policies_workspace_types(ws_types: List[ArkWorkspaceType]) -> List[str]:
    return [serialize_uap_policies_workspace_type(ws_type) for ws_type in ws_types]
