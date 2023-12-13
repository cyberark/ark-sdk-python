from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkDPABaseGeneratePolicy(ArkModel):
    name: Optional[str] = Field(description='Policy name to generate to the workspace')
    disable_edit: bool = Field(description='Whether no interactiveness / editing is required', default=False)
