from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel


class ArkSIACertificatesFilter(ArkModel):
    domain_name: Optional[str] = Field(default=None, description='Filter by domain name')
    cert_name: Optional[str] = Field(default=None, description='Filter by certificate name')
