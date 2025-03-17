from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIARemovePolicies(ArkModel):
    names: Optional[List[str]] = Field(
        default=None, description='Policies to remove from the workspace, if not given, choices will be prompted'
    )
