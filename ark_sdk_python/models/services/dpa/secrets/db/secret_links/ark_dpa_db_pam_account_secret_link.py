from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel


class ArkDPADBPAMAccountSecretLink(ArkModel):
    safe: Optional[str] = Field(description='Safe of the account')
    account_name: Optional[str] = Field(description='Account name')
