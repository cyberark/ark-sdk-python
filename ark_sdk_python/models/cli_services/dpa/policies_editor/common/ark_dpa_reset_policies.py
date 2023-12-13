from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkDPAResetPolicies(ArkModel):
    names: Optional[List[str]] = Field(description='Policy names to reset on the workspace, if not given, all policies are resetted')
    all: bool = Field(description='Whether to reset all locally edited policies', default=False)
