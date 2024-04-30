from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, SecretStr


class ArkDPADBAtlasAccessKeysSecretData(BaseModel):
    public_key: str = Field(description='Public part of mongo atlas access keys')
    private_key: SecretStr = Field(description='Private part of mongo atlas access keys')
    metadata: Optional[Dict[str, Any]] = Field(description='Extra secret details')

    class Config:
        json_encoders = {SecretStr: lambda v: v.get_secret_value() if v else None}


class ArkDPADBExposedAtlasAccessKeysSecretData(BaseModel):
    public_key: str = Field(description='Public part of mongo atlas access keys')
