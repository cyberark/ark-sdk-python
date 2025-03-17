from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIAPoliciesDiff(ArkModel):
    names: Optional[List[str]] = Field(default=None, description='Policy names to show diff on, if not given, shows diff on all policies')
    unified: bool = Field(description='Show all diffs together', default=False)
