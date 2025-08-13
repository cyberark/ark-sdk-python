from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkSIASettingsRDPKeyboardLayout(ArkCamelizedModel):
    layout: Optional[str] = Field(default=None, description="The keyboard layout for RDP sessions.")
