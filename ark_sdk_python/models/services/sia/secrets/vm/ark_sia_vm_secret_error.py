from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIAVMSecretError(ArkModel):
    error: Optional[str] = Field(default=None, description="Error message")
    stack: Optional[str] = Field(default=None, description="Stack trace")
    status_code: Optional[int] = Field(default=None, description="Error status code")
