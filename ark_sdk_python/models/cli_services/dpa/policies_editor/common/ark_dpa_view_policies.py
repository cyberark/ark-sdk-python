from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkDPAViewPolicies(ArkModel):
    names: Optional[List[str]] = Field(description='Policy names to view from the workspace, if not given, choices will be prompted')
    unified: bool = Field(description='Show all requested policies together', default=False)
