from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel


class ArkSIADBPAMAccountSecretLink(ArkModel):
    safe: Optional[str] = Field(default=None, description='Safe of the account')
    account_name: Optional[str] = Field(default=None, description='Account name')
