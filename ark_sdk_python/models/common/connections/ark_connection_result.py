from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkConnectionResult(ArkModel):
    stdout: Optional[str] = Field(description='Stdout of the command')
    stderr: Optional[str] = Field(description='Stderr of the command')
    rc: Optional[int] = Field(description='RC of the command')
