from typing import Optional

from pydantic import Field, SecretStr

from ark_sdk_python.models.ark_model import ArkModel


class ArkSecret(ArkModel):
    secret: Optional[SecretStr] = Field(alias='Secret', description='Secret to be used')

    class Config:
        json_encoders = {SecretStr: lambda v: v.get_secret_value()}
