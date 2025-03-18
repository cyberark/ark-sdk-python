from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from ark_sdk_python.models.ark_model import ArkSecretStr


class ArkSIADBIAMUserSecretData(BaseModel):
    account: str = Field(description='Account number of the iam user')
    region: Optional[str] = Field(default=None, description='Region associated with the iam user')
    username: str = Field(description='Username portion in the ARN of the iam user')
    access_key_id: ArkSecretStr = Field(description='Access key id of the user')
    secret_access_key: ArkSecretStr = Field(description='Secret access key of the user')
    metadata: Optional[Dict[str, Any]] = Field(default=None, description='Extra secret details')


class ArkSIADBExposedIAMUserSecretData(BaseModel):
    account: str = Field(description='Account number of the iam user')
    username: str = Field(description='Username portion in the ARN of the iam user')
