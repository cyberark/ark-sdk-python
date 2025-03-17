from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from ark_sdk_python.models.ark_model import ArkSecretStr


class ArkSIADBAtlasAccessKeysSecretData(BaseModel):
    public_key: str = Field(description='Public part of mongo atlas access keys')
    private_key: ArkSecretStr = Field(description='Private part of mongo atlas access keys')
    metadata: Optional[Dict[str, Any]] = Field(default=None, description='Extra secret details')


class ArkSIADBExposedAtlasAccessKeysSecretData(BaseModel):
    public_key: str = Field(description='Public part of mongo atlas access keys')
