from typing import List, Optional

from pydantic import Field
from typing_extensions import Annotated

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.uap.common.ark_uap_delegation_classification import ArkUAPDelegationClassification
from ark_sdk_python.models.services.uap.common.ark_uap_metadata import ArkUAPMetadata
from ark_sdk_python.models.services.uap.common.ark_uap_principal import ArkUAPPrincipal


class ArkUAPCommonAccessPolicy(ArkCamelizedModel):
    metadata: Annotated[Optional[ArkUAPMetadata], Field(default=None, description='Policy metadata id name and extra information')]
    principals: Annotated[
        Optional[List[ArkUAPPrincipal]], Field(default=None, description='List of users, groups and roles that the policy applies to')
    ]
    delegation_classification: Annotated[
        ArkUAPDelegationClassification,
        Field(default=ArkUAPDelegationClassification.UNRESTRICTED, description='Indicates the user rights for the current policy'),
    ]
