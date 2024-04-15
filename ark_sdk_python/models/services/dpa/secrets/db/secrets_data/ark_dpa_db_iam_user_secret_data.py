from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, SecretStr


class ArkDPADBIAMUserSecretData(BaseModel):
    account: str = Field(description='Account number of the iam user')
    region: Optional[str] = Field(description='Region associated with the iam user')
    username: str = Field(description='Username portion in the ARN of the iam user')
    access_key_id: SecretStr = Field(description='Access key id of the user')
    secret_access_key: SecretStr = Field(description='Secret access key of the user')
    metadata: Optional[Dict[str, Any]] = Field(description='Extra secret details')

    class Config:
        json_encoders = {SecretStr: lambda v: v.get_secret_value() if v else None}


class ArkDPADBExposedIAMUserSecretData(BaseModel):
    account: str = Field(description='Account number of the iam user')
    username: str = Field(description='Username portion in the ARN of the iam user')
