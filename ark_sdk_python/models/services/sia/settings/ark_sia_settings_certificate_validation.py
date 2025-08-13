from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkSIASettingsCertificateValidation(ArkCamelizedModel):
    enabled: Optional[bool] = Field(default=None, description="Specifies whether certificate validation is enabled.")
