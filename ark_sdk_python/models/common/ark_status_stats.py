from typing import List

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel


class ArkStatusStats(ArkModel):
    count: int = Field(description='Amount of tenants in this status')
    ids: List[str] = Field(description='List of their ids')
