from typing import List

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel


class ArkSIABulkDeleteTargetSets(ArkModel):
    target_sets: List[str] = Field(description='List of target sets names to delete')
