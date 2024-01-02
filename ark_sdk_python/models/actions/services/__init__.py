from typing import Any, List

from ark_sdk_python.models.actions.services.ark_dpa_exec_action_consts import DPA_ACTIONS
from ark_sdk_python.models.actions.services.ark_sm_exec_action_consts import SM_ACTIONS

SUPPORTED_SERVICE_ACTIONS: List[Any] = [
    DPA_ACTIONS,
    SM_ACTIONS,
]

__all__ = [
    'DPA_ACTIONS',
    'SM_ACTIONS',
    'SUPPORTED_SERVICE_ACTIONS',
]
