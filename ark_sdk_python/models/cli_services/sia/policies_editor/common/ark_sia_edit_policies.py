from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIAEditPolicies(ArkModel):
    names: Optional[List[str]] = Field(
        default=None, description='Policies to edit from the workspace, if not given, choices will be prompted'
    )
