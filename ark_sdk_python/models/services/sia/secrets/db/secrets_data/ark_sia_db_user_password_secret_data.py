from typing import Any, Dict, Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel, ArkSecretStr


class ArkSIADBUserPasswordSecretData(ArkModel):
    username: Optional[str] = Field(default=None, description='Name or id of the user')
    password: Optional[ArkSecretStr] = Field(default=None, description='Password of the user')
    metadata: Optional[Dict[str, Any]] = Field(default=None, description='Extra secret details')


class ArkSIADBExposedUserPasswordSecretData(ArkModel):
    username: Optional[str] = Field(default=None, description='Name or id of the user')
