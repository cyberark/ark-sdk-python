from typing import Optional

from pydantic import Field, SecretStr

from ark_sdk_python.models import ArkModel


class ArkConnectionCredentials(ArkModel):
    user: Optional[str] = Field(description='Username to connect with')
    password: Optional[SecretStr] = Field(description='Password to use for connection')
    private_key_filepath: Optional[str] = Field(description='Private key file path to use for the connection')
    private_key_contents: Optional[str] = Field(description='Private key contents to use for the connection')
