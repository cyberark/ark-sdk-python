from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkWinRMConnectionData(ArkModel):
    certificate: Optional[str] = Field(description="Certificate to use for connection transport", default=None)
    validate_certificate: bool = Field(description="Whether to validate the SSL certificate", default=True)
