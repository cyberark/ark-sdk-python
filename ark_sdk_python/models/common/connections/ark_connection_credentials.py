from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel, ArkSecretStr


class ArkConnectionCredentials(ArkModel):
    user: Optional[str] = Field(description='Username to connect with', default=None)
    password: Optional[ArkSecretStr] = Field(description='Password to use for connection', default=None)
    private_key_filepath: Optional[str] = Field(description='Private key file path to use for the connection', default=None)
    private_key_contents: Optional[str] = Field(description='Private key contents to use for the connection', default=None)
