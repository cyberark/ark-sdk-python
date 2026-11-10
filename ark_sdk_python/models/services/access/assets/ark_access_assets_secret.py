from typing import Optional

from pydantic import Field
from ark_sdk_python.models.ark_model import ArkCamelizedModel, ArkModel


class ArkAccessAssetsSecretRequest(ArkModel):
    asset_id: str = Field(description='Asset identifier', min_length=1)
    reason: Optional[str] = Field(description='Reason for retrieving the secret', default=None)


class ArkAccessAssetsSecretResponse(ArkCamelizedModel):
    asset_id: str = Field(description='Asset identifier', min_length=1)
    secret: str = Field(description='Secret value')
    security_message: Optional[str] = Field(default=None, description='Security guidelines for users handling sensitive information')
