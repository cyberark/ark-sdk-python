from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkSIASettingsRDPRecording(ArkCamelizedModel):
    enabled: Optional[bool] = Field(default=None, description="Is SIA RDP recording enabled")
