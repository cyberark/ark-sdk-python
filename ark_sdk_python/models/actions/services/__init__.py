from typing import Any, List

from ark_sdk_python.models.actions.services.ark_dpa_exec_action_consts import DPA_ACTIONS
from ark_sdk_python.models.actions.services.ark_identity_exec_action_consts import IDENTITY_ACTIONS
from ark_sdk_python.models.actions.services.ark_sm_exec_action_consts import SM_ACTIONS

SUPPORTED_SERVICE_ACTIONS: List[Any] = [
    IDENTITY_ACTIONS,
    DPA_ACTIONS,
    SM_ACTIONS,
]

__all__ = [
    'IDENTITY_ACTIONS',
    'DPA_ACTIONS',
    'SM_ACTIONS',
    'SUPPORTED_SERVICE_ACTIONS',
]
