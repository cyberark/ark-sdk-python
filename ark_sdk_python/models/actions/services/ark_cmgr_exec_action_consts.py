from typing import Dict, Final, Optional, Type

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.actions.ark_service_action_definition import ArkServiceActionDefinition
from ark_sdk_python.models.services.cmgr import (
    ArkCmgrAddNetwork,
    ArkCmgrAddPool,
    ArkCmgrAddPoolBulkIdentifier,
    ArkCmgrAddPoolSingleIdentifier,
    ArkCmgrDeleteNetwork,
    ArkCmgrDeletePool,
    ArkCmgrDeletePoolBulkIdentifier,
    ArkCmgrDeletePoolSingleIdentifier,
    ArkCmgrGetNetwork,
    ArkCmgrGetPool,
    ArkCmgrGetPoolComponent,
    ArkCmgrListPoolIdentifiers,
    ArkCmgrNetworksFilter,
    ArkCmgrPoolComponentsFilter,
    ArkCmgrPoolIdentifiersFilter,
    ArkCmgrPoolsFilter,
    ArkCmgrUpdateNetwork,
    ArkCmgrUpdatePool,
)

# Component Manager Definitions
CMGR_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'add-network': ArkCmgrAddNetwork,
    'update-network': ArkCmgrUpdateNetwork,
    'delete-network': ArkCmgrDeleteNetwork,
    'list-networks': None,
    'list-networks-by': ArkCmgrNetworksFilter,
    'network': ArkCmgrGetNetwork,
    'networks-stats': None,
    'add-pool': ArkCmgrAddPool,
    'update-pool': ArkCmgrUpdatePool,
    'delete-pool': ArkCmgrDeletePool,
    'list-pools': None,
    'list-pools-by': ArkCmgrPoolsFilter,
    'pool': ArkCmgrGetPool,
    'pools-stats': None,
    'add-pool-identifier': ArkCmgrAddPoolSingleIdentifier,
    'add-pool-identifiers': ArkCmgrAddPoolBulkIdentifier,
    'delete-pool-identifier': ArkCmgrDeletePoolSingleIdentifier,
    'delete-pool-identifiers': ArkCmgrDeletePoolBulkIdentifier,
    'list-pool-identifiers': ArkCmgrListPoolIdentifiers,
    'list-pool-identifiers-by': ArkCmgrPoolIdentifiersFilter,
    'list-pools-components': None,
    'list-pools-components-by': ArkCmgrPoolComponentsFilter,
    'pool-component': ArkCmgrGetPoolComponent,
}

# Service Actions Definition
CMGR_ACTIONS: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='cmgr',
    schemas=CMGR_ACTION_TO_SCHEMA_MAP,
)
