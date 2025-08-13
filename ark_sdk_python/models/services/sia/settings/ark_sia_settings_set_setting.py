from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.services.sia.settings.ark_sia_settings_feature_name import ArkSIASettingsFeatureName
from ark_sdk_python.models.services.sia.settings.ark_sia_settings_setting_types import ArkSIASettingsSettingTypes


class ArkSIASettingsSetSetting(ArkModel):
    feature_name: ArkSIASettingsFeatureName = Field(description="Name of feature to set")
    setting: ArkSIASettingsSettingTypes = Field(description="The settings to set")
