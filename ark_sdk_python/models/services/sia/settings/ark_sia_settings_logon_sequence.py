from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkSIASettingsLogonSequence(ArkCamelizedModel):
    logon_sequence: Optional[str] = Field(default=None, description='Configuration for the tenant logon sequence')
