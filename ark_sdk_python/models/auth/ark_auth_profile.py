from typing import Any, Optional

from pydantic import Field, SerializeAsAny, TypeAdapter, ValidationInfo, field_validator

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.auth.ark_auth_method import (
    ArkAuthMethod,
    ArkAuthMethodSettings,
    ArkAuthMethodSettingsMap,
    ArkAuthMethodSettingsTypes,
    DefaultArkAuthMethodSettings,
)


class ArkAuthProfile(ArkModel):
    username: Optional[str] = Field(default=None, description='Username to authenticate with', alias='Username')
    auth_method: ArkAuthMethod = Field(
        description='Authentication type to use when an authenticator supports multiple types',
        alias='Authentication Method',
        default=ArkAuthMethod.Default,
    )
    auth_method_settings: SerializeAsAny[ArkAuthMethodSettings] = Field(
        description='Authentication method settings used for the authenticator',
        alias='Authentication Method Settings',
        default_factory=DefaultArkAuthMethodSettings,
    )

    # pylint: disable=no-self-use,no-self-argument
    @field_validator('auth_method_settings', mode='before')
    def parse_method_settings(cls, v: Any, validation_info: ValidationInfo) -> Any:
        if 'auth_method' in validation_info.data:
            return ArkAuthMethodSettingsMap[validation_info.data['auth_method']].model_validate(v)
        return TypeAdapter(ArkAuthMethodSettingsTypes).validate_python(v)
