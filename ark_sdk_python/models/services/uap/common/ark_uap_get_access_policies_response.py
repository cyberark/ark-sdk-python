from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel
from ark_sdk_python.models.services.uap.common.ark_uap_common_access_policy import ArkUAPCommonAccessPolicy


class ArkUAPPolicyResultsResponse(ArkCamelizedModel):
    results: List[ArkUAPCommonAccessPolicy] = Field(description='List of policies')
    next_token: Optional[str] = Field(default=None, description='Token for the next page of results')
    total: int = Field(description='Total number of policies available')
