from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkDPAGetPoliciesStatus(ArkModel):
    names: Optional[List[str]] = Field(description='Policy names to show status on, if not given, shows status on all policies')
