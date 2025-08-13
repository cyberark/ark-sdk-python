from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.services.sia.settings.ark_sia_settings_feature_name import ArkSIASettingsFeatureName


class ArkSIASettingsGetSetting(ArkModel):
    feature_name: ArkSIASettingsFeatureName = Field(description='Name of the Feature to get')
