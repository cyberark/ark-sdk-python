from typing import Any, Dict, Optional

from pydantic import Field, SecretStr

from ark_sdk_python.models.ark_model import ArkModel


class ArkDPADBUserPasswordSecretData(ArkModel):
    username: Optional[str] = Field(description='Name or id of the user')
    password: Optional[SecretStr] = Field(description='Password of the user')
    metadata: Optional[Dict[str, Any]] = Field(description='Extra secret details')

    class Config:
        json_encoders = {SecretStr: lambda v: v.get_secret_value() if v else None}


class ArkDPADBExposedUserPasswordSecretData(ArkModel):
    username: Optional[str] = Field(description='Name or id of the user')
