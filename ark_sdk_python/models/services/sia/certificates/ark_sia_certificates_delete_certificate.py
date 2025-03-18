from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIADeleteCertificate(ArkModel):
    certificate_id: str = Field(description='ID of the certificate to delete', min_length=1)
