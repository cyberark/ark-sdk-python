from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkDPARemovePolicies(ArkModel):
    names: Optional[List[str]] = Field(description='Policies to remove from the workspace, if not given, choices will be prompted')
