from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel


class ArkSIABulkTargetSetItemResult(ArkModel):
    strong_account_id: Optional[str] = Field(default=None, description='The strong account related to the bulk add')
    target_set_name: str = Field(description='The target set item name')
    success: bool = Field(description='Whether the operation was successful or not')


class ArkSIABulkTargetSetResponse(ArkModel):
    results: List[ArkSIABulkTargetSetItemResult] = Field(description='List of results for the target set bulk operation')
