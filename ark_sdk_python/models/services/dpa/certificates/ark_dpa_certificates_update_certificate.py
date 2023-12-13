from pydantic import Field, FilePath

from ark_sdk_python.models.services.dpa.certificates.ark_dpa_certificates_certificate import ArkDPACreateCertificateBase


class ArkDPAUpdateCertificate(ArkDPACreateCertificateBase):
    certificate_id: str = Field(description='ID of the certificate to update', min_length=1)
    file: FilePath = Field(description='Path to a file with the certificate body')


class ArkDPAUpdateCertificateRequest(ArkDPACreateCertificateBase):
    cert_body: str = Field(description='Certificate body content', min_length=1)
