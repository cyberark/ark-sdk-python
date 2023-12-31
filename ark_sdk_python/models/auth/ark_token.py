from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import Field, SecretStr

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.auth.ark_auth_method import ArkAuthMethod


class ArkTokenType(str, Enum):
    JWT = 'JSON Web Token'
    Cookies = 'Cookies'
    Token = 'Token'
    Password = 'Password'
    Custom = 'Custom'
    Internal = 'Internal'


class ArkToken(ArkModel):
    token: SecretStr = Field(description='Actual token', alias='Token')
    username: Optional[str] = Field(description='Username whos token is related to', alias='Username')
    endpoint: Optional[str] = Field(description='Endpoint associated with the token', alias='Authentication Endpoint')
    token_type: ArkTokenType = Field(description='Token type', alias='Token Type', default=ArkTokenType.JWT)
    auth_method: Optional[ArkAuthMethod] = Field(description='The authenticaton method type of this token', alias='Authentication Method')
    expires_in: Optional[datetime] = Field(description='When the token will expire', alias='Expires In')
    refresh_token: Optional[str] = Field(description='Refresh token used for refreshing the existing token', alias='Refresh Token')
    metadata: Dict[str, Any] = Field(description='Token metadata', alias='Token Metadata', default_factory=dict)

    class Config:
        json_encoders = {SecretStr: lambda v: v.get_secret_value()}
