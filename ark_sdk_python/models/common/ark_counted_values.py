from typing import Any, List

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel


class ArkCountedValues(ArkModel):
    count: int = Field(description='Count of the values')
    values: List[Any] = Field(description='The values themselves')
