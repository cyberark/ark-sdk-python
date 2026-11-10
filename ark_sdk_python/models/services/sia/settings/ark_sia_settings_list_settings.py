from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel


class ArkSIASettingsListSettings(ArkModel):
    default: bool = Field(
        description='Return the environment default settings instead of the tenant\'s effective settings',
        default=False,
    )
