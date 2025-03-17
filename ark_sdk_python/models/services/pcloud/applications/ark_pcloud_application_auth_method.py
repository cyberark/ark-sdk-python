from enum import Enum
from typing import List, Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel, ArkTitleizedModel


class ArkPCloudApplicationAuthMethodType(str, Enum):
    Hash = 'hash'
    OsUser = 'osUser'
    IP = 'machineAddress'
    Path = 'path'
    CertificateSerialNumber = 'certificateSerialNumber'
    Kubernetes = 'Kubernetes'
    Certificate = 'certificateattr'


class ArkPCloudApplicationAuthMethodCertKeyVal(ArkModel):
    key: str = Field(description='Key of the field')
    value: str = Field(description='Value of the field')


class ArkPCloudApplicationAuthMethod(ArkTitleizedModel):
    auth_id: str = Field(description='ID of the auth method', alias='authID')
    auth_type: ArkPCloudApplicationAuthMethodType = Field(description='Type of the authentication')

    # Applied for Certificate serial number, ip, os user, hash, path
    auth_value: Optional[str] = Field(default=None, description='Value of the authentication')

    # Path type extras
    is_folder: Optional[bool] = Field(default=None, description='For path in the machine, whether its a folder or not')
    allow_internal_scripts: Optional[bool] = Field(default=None, description='Whether internal scripts are allowed on the folder or not')

    # Hash, certificate serial number, certificate type extras
    comment: Optional[str] = Field(default=None, description='Comment for the hash')

    # Kubernetes type extras, only one of them should exist
    namespace: Optional[str] = Field(default=None, description='Kube namespace')
    image: Optional[str] = Field(default=None, description='Kube container image')
    env_var_name: Optional[str] = Field(default=None, description='Kube env var name')
    env_var_value: Optional[str] = Field(default=None, description='Kube env var value')

    # Certificate type extras
    subject: Optional[List[ArkPCloudApplicationAuthMethodCertKeyVal]] = Field(default=None, description='Subject of the certificate')
    issuer: Optional[List[ArkPCloudApplicationAuthMethodCertKeyVal]] = Field(default=None, description='Issuer of the certificate')
    subject_alternative_name: Optional[List[ArkPCloudApplicationAuthMethodCertKeyVal]] = Field(
        default=None, description='SAN of the certificate'
    )
