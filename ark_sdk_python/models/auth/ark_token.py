from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel, ArkSecretStr
from ark_sdk_python.models.auth.ark_auth_method import ArkAuthMethod


class ArkTokenType(str, Enum):
    JWT = 'JSON Web Token'
    Cookies = 'Cookies'
    Token = 'Token'
    Password = 'Password'
    Custom = 'Custom'
    Internal = 'Internal'


class ArkToken(ArkModel):
    token: ArkSecretStr = Field(description='Actual token', alias='Token')
    username: Optional[str] = Field(default=None, description='Username whos token is related to', alias='Username')
    endpoint: Optional[str] = Field(default=None, description='Endpoint associated with the token', alias='Authentication Endpoint')
    token_type: ArkTokenType = Field(description='Token type', alias='Token Type', default=ArkTokenType.JWT)
    auth_method: Optional[ArkAuthMethod] = Field(
        default=None, description='The authenticaton method type of this token', alias='Authentication Method'
    )
    expires_in: Optional[datetime] = Field(default=None, description='When the token will expire', alias='Expires In')
    refresh_token: Optional[str] = Field(
        default=None, description='Refresh token used for refreshing the existing token', alias='Refresh Token'
    )
    metadata: Dict[str, Any] = Field(description='Token metadata', alias='Token Metadata', default_factory=dict)
    origin_verify: Optional[str] = Field(default=None, description='Origin verify', alias='Origin Verify')
