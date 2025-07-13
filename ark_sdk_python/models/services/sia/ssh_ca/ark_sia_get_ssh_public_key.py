from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIAGetSSHPublicKey(ArkModel):
    output_file: Optional[str] = Field(default=None, description='Save output to file')
