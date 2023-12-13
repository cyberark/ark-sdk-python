from typing import List

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkDPAPoliciesStatus(ArkModel):
    modified_policies: List[str] = Field(description='List of locally modified policies')
    removed_policies: List[str] = Field(description='List of locally removed policies')
    added_policies: List[str] = Field(description='List of locally added policies')
