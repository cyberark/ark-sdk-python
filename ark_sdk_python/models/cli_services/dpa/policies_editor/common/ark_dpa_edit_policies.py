from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkDPAEditPolicies(ArkModel):
    names: Optional[List[str]] = Field(description='Policies to edit from the workspace, if not given, choices will be prompted')
