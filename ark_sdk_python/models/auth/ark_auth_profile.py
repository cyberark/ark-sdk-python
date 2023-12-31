from typing import Optional

from pydantic import Field, parse_obj_as, validator

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.auth.ark_auth_method import (
    ArkAuthMethod,
    ArkAuthMethodSettings,
    ArkAuthMethodSettingsMap,
    ArkAuthMethodSettingsTypes,
    DefaultArkAuthMethodSettings,
)


class ArkAuthProfile(ArkModel):
    username: Optional[str] = Field(description='Username to authenticate with', alias='Username')
    auth_method: ArkAuthMethod = Field(
        description='Authentication type to use when an authenticator supports multiple types',
        alias='Authentication Method',
        default=ArkAuthMethod.Default,
    )
    auth_method_settings: ArkAuthMethodSettings = Field(
        description='Authentication method settings used for the authenticator',
        alias='Authentication Method Settings',
        default_factory=DefaultArkAuthMethodSettings,
    )

    # pylint: disable=no-self-use,no-self-argument
    @validator('auth_method_settings', pre=True, always=True, allow_reuse=True)
    def parse_method_settings(cls, v, values):
        if 'auth_method' in values:
            return ArkAuthMethodSettingsMap[values['auth_method']].parse_obj(v)
        return parse_obj_as(ArkAuthMethodSettingsTypes, v)
