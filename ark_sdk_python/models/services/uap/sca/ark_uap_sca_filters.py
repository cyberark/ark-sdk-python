from typing import List

from pydantic import Field

from ark_sdk_python.models.common import ArkCategoryType
from ark_sdk_python.models.services.uap.common.ark_uap_get_access_policies_request import ArkUAPFilters


class ArkUAPSCAFilters(ArkUAPFilters):
    """
    This module defines filters specific to the SCA (Security Cloud Access) policies
    within the UAP (Unified Access Policies) service.

    You can set the following fields:

    - target_category: Optional[List[ArkCategoryType]]
        A list of target categories to filter the policies by.

    - policy_type: Optional[List[ArkUAPPolicyType]]
        A list of policy types to filter the policies by.

    - policy_tags: Optional[List[str]]
        A list of policy tags to filter the policies by.

    - identities: Optional[List[str]]
        A list of identities to filter the policies by.

    - status: Optional[List[ArkUAPStatusType]]
        A list of policy statuses to filter the policies by.

    - text_search: Optional[str]
        A text value to apply as a search filter across policies.

    - show_editable_policies: Optional[bool]
        Whether to show only policies that are editable by the current user.
    """

    target_category: List[ArkCategoryType] = Field(
        default=[ArkCategoryType.CLOUD_CONSOLE], description="Target category is fixed to Cloud Console"
    )

    def __setattr__(self, name, value):
        if name == "target_category" and value != [ArkCategoryType.CLOUD_CONSOLE]:
            raise ValueError("target_category is final and cannot be modified.")
        super().__setattr__(name, value)
