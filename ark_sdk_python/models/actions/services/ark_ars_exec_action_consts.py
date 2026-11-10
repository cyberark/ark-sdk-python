from typing import Dict, Final, List, Optional, Type

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.actions.ark_service_action_definition import ArkServiceActionDefinition
from ark_sdk_python.models.services.ars.common import ArkARSFilter
from ark_sdk_python.models.services.ars.requests import ArkARSCancelAccessRequest, ArkARSFinalizeAccessRequest, ArkARSGetAccessRequest

# ARS Definitions
# Requests
ARS_REQUESTS_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'cancel-access-request': ArkARSCancelAccessRequest,
    'finalize-access-request': ArkARSFinalizeAccessRequest,
    'list-access-requests': None,
    'list-access-requests-by': ArkARSFilter,
    'access-request': ArkARSGetAccessRequest,
    'access-requests-stats': None,
}
ARS_REQUESTS_ASYNC_ACTIONS: Final[List[str]] = [
    'cancel-access-request',
    'finalize-access-request',
]
ARS_REQUESTS_ACTIONS: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='requests',
    schemas=ARS_REQUESTS_ACTION_TO_SCHEMA_MAP,
    async_actions=ARS_REQUESTS_ASYNC_ACTIONS,
)

# Service Actions Definition
ARS_ACTIONS: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='ars',
    subactions=[
        ARS_REQUESTS_ACTIONS,
    ],
)
