from typing import Any, Dict, Union

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIADBGeneratedAssets(ArkModel):
    assets: Union[str, Dict[str, Any]] = Field(description='Actual assets')
