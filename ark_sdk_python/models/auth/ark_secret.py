from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel, ArkSecretStr


class ArkSecret(ArkModel):
    secret: Optional[ArkSecretStr] = Field(default=None, alias='Secret', description='Secret to be used')
