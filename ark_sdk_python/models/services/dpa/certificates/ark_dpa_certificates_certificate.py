from enum import Enum
from typing import Any, Dict, Optional

from pydantic import Field, FilePath, PositiveInt

from ark_sdk_python.models import ArkCamelizedModel, ArkModel


class CertificateTypes(str, Enum):
    PFX = 'PFX'
    P12 = 'P12'
    PEM = 'PEM'


class CertificateMetadata(ArkCamelizedModel):
    issuer: str = Field(description='Certificate issuer', default=None)
    subject: str = Field(description='Certificate subject', default=None)
    valid_from: str = Field(description='Certificate valid from date', default=None)
    valid_to: str = Field(description='Certificate valid to date', default=None)
    serial_number: str = Field(description='Certificate serial number', default=None)


class ArkDPACreateCertificateBase(ArkModel):
    cert_type: CertificateTypes = Field(description='Certificate type i.e. PEM, p7b, pfx', min_length=1)
    cert_password: Optional[str] = Field(default=None, description='Encryption password for certificate')
    cert_name: Optional[str] = Field(default=None, description='Name of the certificate')
    cert_description: Optional[str] = Field(default=None, description='Description of the certificate')
    domain_name: Optional[str] = Field(default=None, description='Domain to which the certificate is assigned')
    labels: Optional[Dict[str, Any]] = Field(default=None, description='Additional labels assigned to the certificate')


class ArkDPACreateCertificateRequest(ArkDPACreateCertificateBase):
    cert_body: str = Field(description='Certificate body content', min_length=1)


class ArkDPACreateCertificate(ArkDPACreateCertificateBase):
    file: FilePath = Field(description='Path to a file with the certificate body')


class ArkDPACertificate(ArkModel):
    tenant_id: str = Field(description='ID of the tenant')
    certificate_id: str = Field(description='ID of the certificate', min_length=1)
    domain_name: Optional[str] = Field(default=None, description='Domain to which the certificate is assigned')
    cert_body: str = Field(description='Certificate body content')
    cert_name: Optional[str] = Field(default=None, description='Name of the certificate')
    cert_description: Optional[str] = Field(default=None, description='Description of the certificate')
    expiration_date: str = Field(description='Time when certificate will expire', min_length=1)
    created_by: Optional[str] = Field(description='Author of the certificate entry')
    last_updated_by: Optional[str] = Field(description='Author of last certificate entry update')
    checksum: str = Field(description='Checksum calculated from the certificate content', min_length=1)
    version: PositiveInt = Field(description='Version of the certificate')
    metadata: CertificateMetadata = Field(description='Metadata of the certificate')
    updated_time: str = Field(description='Datetime of the last certificate update')
    labels: Optional[Dict[str, Any]] = Field(default=None, description='Additional labels assigned to the certificate')


class ArkDPAShortCertificate(ArkModel):
    certificate_id: str = Field(description='ID of the Certificate', min_length=1)
    body: str = Field(default=None, description='Certificate body content', min_length=1)
    domain: Optional[str] = Field(default=None, description='Domain to which the certificate is assigned')
    cert_name: Optional[str] = Field(default=None, description='Name of the certificate')
    cert_description: Optional[str] = Field(default=None, description='Description of the certificate')
    metadata: CertificateMetadata = Field(description='Metadata of the certificate')
    labels: Optional[Dict[str, Any]] = Field(default=None, description='Additional labels assigned to the certificate')
