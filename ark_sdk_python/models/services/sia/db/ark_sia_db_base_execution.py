from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIADBBaseExecution(ArkModel):
    target_address: str = Field(description='Target address to connect to')
    target_username: Optional[str] = Field(default=None, description='Target username account to use')
