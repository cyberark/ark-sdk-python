from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIASSOGetSSHKey(ArkModel):
    folder: Optional[str] = Field(default=None, description='Output folder to save the key to')
