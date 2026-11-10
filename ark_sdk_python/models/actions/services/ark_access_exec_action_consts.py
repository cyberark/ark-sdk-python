from typing import Dict, Final, Optional, Type

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.actions.ark_service_action_definition import ArkServiceActionDefinition
from ark_sdk_python.models.services.access.assets import ArkAccessAssetsListAssets, ArkAccessAssetsSecretRequest

ASSETS_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'list': ArkAccessAssetsListAssets,
    'secret': ArkAccessAssetsSecretRequest,
}

ASSETS_ACTION: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='assets',
    schemas=ASSETS_ACTION_TO_SCHEMA_MAP,
)

ACCESS_ACTIONS: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='access',
    subactions=[ASSETS_ACTION],
)
