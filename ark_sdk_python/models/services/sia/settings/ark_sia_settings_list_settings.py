from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel


class ArkSIASettingsListSettings(ArkModel):
    default: bool = Field(description='Should include default settings', default=True)
