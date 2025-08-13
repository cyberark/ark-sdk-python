from typing import Dict, Final, Optional, Type

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.actions.ark_service_action_definition import ArkServiceActionDefinition
from ark_sdk_python.models.services.uap.common import ArkUAPFilters
from ark_sdk_python.models.services.uap.common.ark_uap_delete_policy_request import ArkUAPDeletePolicyRequest
from ark_sdk_python.models.services.uap.common.ark_uap_get_policy_request import ArkUAPGetPolicyRequest
from ark_sdk_python.models.services.uap.common.ark_uap_get_policy_status import ArkUAPGetPolicyStatus
from ark_sdk_python.models.services.uap.sca.ark_uap_sca_cloud_console_access_policy import ArkUAPSCACloudConsoleAccessPolicy
from ark_sdk_python.models.services.uap.sca.ark_uap_sca_filters import ArkUAPSCAFilters
from ark_sdk_python.models.services.uap.sia.db.ark_uap_sia_db_access_policy import ArkUAPSIADBAccessPolicy
from ark_sdk_python.models.services.uap.sia.db.ark_uap_sia_db_filters import ArkUAPSIADBFilters
from ark_sdk_python.models.services.uap.sia.vm import ArkUAPSIAVMAccessPolicy, ArkUAPSIAVMFilters

# SCA Definitions
UAP_SCA_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'add-policy': ArkUAPSCACloudConsoleAccessPolicy,
    'delete-policy': ArkUAPDeletePolicyRequest,
    'update-policy': ArkUAPSCACloudConsoleAccessPolicy,
    'policy': ArkUAPGetPolicyRequest,
    'list-policies': None,
    'list-policies-by': ArkUAPSCAFilters,
    'policies-stats': None,
    'policy-status': ArkUAPGetPolicyStatus,
}

# Service Actions Definition
UAP_SCA_ACTIONS: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='sca',
    schemas=UAP_SCA_ACTION_TO_SCHEMA_MAP,
)

# SIA DB Definitions
UAP_SIA_DB_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'add-policy': ArkUAPSIADBAccessPolicy,
    'delete-policy': ArkUAPDeletePolicyRequest,
    'update-policy': ArkUAPSIADBAccessPolicy,
    'policy': ArkUAPGetPolicyRequest,
    'list-policies': None,
    'list-policies-by': ArkUAPSIADBFilters,
    'policies-stats': None,
    'policy-status': ArkUAPGetPolicyStatus,
}

# Service Actions Definition
UAP_SIA_DB_ACTIONS: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='db',
    schemas=UAP_SIA_DB_ACTION_TO_SCHEMA_MAP,
)

# SIA VM Definitions
UAP_SIA_VM_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'add-policy': ArkUAPSIAVMAccessPolicy,
    'delete-policy': ArkUAPDeletePolicyRequest,
    'update-policy': ArkUAPSIAVMAccessPolicy,
    'policy': ArkUAPGetPolicyRequest,
    'list-policies': None,
    'list-policies-by': ArkUAPSIAVMFilters,
    'policies-stats': None,
    'policy-status': ArkUAPGetPolicyStatus,
}

# Service Actions Definition
UAP_SIA_VM_ACTIONS: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='vm',
    schemas=UAP_SIA_VM_ACTION_TO_SCHEMA_MAP,
)

# UAP Definitions
UAP_ACTION_TO_SCHEMA_MAP: Final[Dict[str, Optional[Type[ArkModel]]]] = {
    'policies-stats': None,
    'list-policies': None,
    'list-policies-by': ArkUAPFilters,
    'policy-status': ArkUAPGetPolicyStatus,
}


UAP_ACTIONS: Final[ArkServiceActionDefinition] = ArkServiceActionDefinition(
    action_name='uap',
    schemas=UAP_ACTION_TO_SCHEMA_MAP,
    subactions=[
        UAP_SCA_ACTIONS,
        UAP_SIA_DB_ACTIONS,
        UAP_SIA_VM_ACTIONS,
    ],
)
