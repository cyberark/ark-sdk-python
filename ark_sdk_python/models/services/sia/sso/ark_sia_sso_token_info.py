from typing import Any, Dict

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIASSOTokenInfo(ArkModel):
    metadata: Dict[str, Any] = Field(description='Token metadata')
