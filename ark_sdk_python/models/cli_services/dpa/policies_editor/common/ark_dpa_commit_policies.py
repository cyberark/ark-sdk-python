from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkDPACommitPolicies(ArkModel):
    names: Optional[List[str]] = Field(
        description='Policy names to commit from the workspace to the remote, if not given, choices will be prompted'
    )
    all: bool = Field(description='Whether to commit all locally edited policies', default=False)
