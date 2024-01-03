from typing import Any, Dict, Final, Optional, Type

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.actions.ark_service_action_definition import ArkServiceActionDefinition
from ark_sdk_python.models.services.sm import ArkSMGetSession, ArkSMGetSessionActivities, ArkSMSessionActivitiesFilter, ArkSMSessionsFilter

# Session Monitoring Definitions
SM_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'list-sessions': None,
    'count-sessions': None,
    'list-sessions-by': ArkSMSessionsFilter,
    'count-sessions-by': ArkSMSessionsFilter,
    'session': ArkSMGetSession,
    'list-session-activities': ArkSMGetSessionActivities,
    'count-session-activities': ArkSMGetSessionActivities,
    'list-session-activities-by': ArkSMSessionActivitiesFilter,
    'count-session-activities-by': ArkSMSessionActivitiesFilter,
    'sessions-stats': None,
}
SM_ACTION_DEFAULTS_MAP: Final[Dict[str, Dict[str, Any]]] = {}

# Service Actions Definition
SM_ACTIONS: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='sm',
    schemas=SM_ACTION_TO_SCHEMA_MAP,
    defaults=SM_ACTION_DEFAULTS_MAP,
)
