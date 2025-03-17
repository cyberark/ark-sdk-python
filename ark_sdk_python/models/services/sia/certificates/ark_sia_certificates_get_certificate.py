from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel


class ArkSIAGetCertificate(ArkModel):
    certificate_id: str = Field(description='ID of the certificate', min_length=1)
