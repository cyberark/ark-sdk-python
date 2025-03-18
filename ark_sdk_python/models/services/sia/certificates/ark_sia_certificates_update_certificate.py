from pydantic import Field, FilePath

from ark_sdk_python.models.services.sia.certificates.ark_sia_certificates_certificate import ArkSIACreateCertificateBase


class ArkSIAUpdateCertificate(ArkSIACreateCertificateBase):
    certificate_id: str = Field(description='ID of the certificate to update', min_length=1)
    file: FilePath = Field(description='Path to a file with the certificate body')


class ArkSIAUpdateCertificateRequest(ArkSIACreateCertificateBase):
    cert_body: str = Field(description='Certificate body content', min_length=1)
