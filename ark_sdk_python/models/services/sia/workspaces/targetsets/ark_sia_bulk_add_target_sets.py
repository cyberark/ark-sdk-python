from typing import List

from pydantic import Field

from ark_sdk_python.models import ArkModel
from ark_sdk_python.models.services.sia.workspaces.targetsets.ark_sia_add_target_set import ArkSIAAddTargetSet


class ArkSIABulkAddTargetSetsItem(ArkModel):
    strong_account_id: str = Field(description='Secret ID of the strong account related to this set')
    target_sets: List[ArkSIAAddTargetSet] = Field(description='The target sets to associate with the strong account')


class ArkSIABulkAddTargetSets(ArkModel):
    target_sets_mapping: List[ArkSIABulkAddTargetSetsItem] = Field(description='Bulk of target set mappings to add')
