from typing import Any, List

from ark_sdk_python.models.actions.services.ark_cmgr_exec_action_consts import CMGR_ACTIONS
from ark_sdk_python.models.actions.services.ark_identity_exec_action_consts import IDENTITY_ACTIONS
from ark_sdk_python.models.actions.services.ark_pcloud_exec_action_consts import PCLOUD_ACTIONS
from ark_sdk_python.models.actions.services.ark_sia_exec_action_consts import SIA_ACTIONS
from ark_sdk_python.models.actions.services.ark_sm_exec_action_consts import SM_ACTIONS
from ark_sdk_python.models.actions.services.ark_uap_exec_action_consts import UAP_ACTIONS

SUPPORTED_SERVICE_ACTIONS: List[Any] = [
    UAP_ACTIONS,
    IDENTITY_ACTIONS,
    SIA_ACTIONS,
    SM_ACTIONS,
    PCLOUD_ACTIONS,
    CMGR_ACTIONS,
]

__all__ = [
    'IDENTITY_ACTIONS',
    'SIA_ACTIONS',
    'SM_ACTIONS',
    'PCLOUD_ACTIONS',
    'CMGR_ACTIONS',
    'SUPPORTED_SERVICE_ACTIONS',
]
