from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkDPADBBaseExecution(ArkModel):
    target_address: str = Field(description='Target address to connect to')
    target_username: Optional[str] = Field(description='Target username account to use')
