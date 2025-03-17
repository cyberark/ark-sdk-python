from typing import Any, Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIASSOAcquireTokenResponse(ArkModel):
    token: Dict[str, Any] = Field(description='Token data')
    metadata: Dict[str, Any] = Field(description='Token metadata')
