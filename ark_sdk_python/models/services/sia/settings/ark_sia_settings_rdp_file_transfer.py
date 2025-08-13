from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkSIASettingsRDPFileTransfer(ArkCamelizedModel):
    enabled: Optional[bool] = Field(default=None, description="Specifies whether RDP file transfer is enabled.")
