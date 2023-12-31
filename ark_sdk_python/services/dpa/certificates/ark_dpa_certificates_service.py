from http import HTTPStatus
from typing import Final, List

from overrides import overrides
from pydantic.error_wrappers import ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.dpa.certificates import (
    ArkDPACertificate,
    ArkDPACertificatesFilter,
    ArkDPACreateCertificate,
    ArkDPACreateCertificateRequest,
    ArkDPADeleteCertificate,
    ArkDPAGetCertificate,
    ArkDPAShortCertificate,
    ArkDPAUpdateCertificate,
    ArkDPAUpdateCertificateRequest,
)
from ark_sdk_python.services.ark_service import ArkService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='dpa-certificates', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
CERTIFICATES_API: Final[str] = 'api/certificates'
CERTIFICATE_API: Final[str] = 'api/certificates/{certificate_id}'


class ArkDPACertificatesService(ArkService):
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        super().__init__(isp_auth)
        self.__isp_auth = isp_auth
        self.__client: ArkISPServiceClient = ArkISPServiceClient.from_isp_auth(self.__isp_auth, 'dpa')

    def add_certificate(self, create_certificate: ArkDPACreateCertificate) -> ArkDPACertificate:
        """
        Adds a new certificate through the Access Certificates Service.

        Args:
            create_certificate (ArkDPACreateCertificate): The certificate to add

        Raises:
            ArkServiceException: When the certificate could not be added

        Returns:
            ArkDPACertificate: The added certificate
        """
        self._logger.info("Adding new certificate.")
        cert_body = ''
        try:
            with open(create_certificate.file, 'r', encoding='utf-8') as f:
                cert_body = f.read()
        except Exception as ex:
            raise ArkServiceException(f'Failed to read certificate file [{create_certificate.file}] [{str(ex)}]') from ex
        if not cert_body:
            raise ArkServiceException(f'Certificate file [{create_certificate.file}] is empty')
        create_certificate_req = ArkDPACreateCertificateRequest(cert_body=cert_body, **create_certificate.dict()).dict()
        resp = self.__client.post(CERTIFICATES_API, json=create_certificate_req)
        if resp.status_code == HTTPStatus.CREATED:
            try:
                cert_id = resp.json()['certificate_id']
                return self.certificate(ArkDPAGetCertificate(certificate_id=cert_id))
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f"Failed to parse response from create certificate [{str(ex)}]")
                raise ArkServiceException(f"Failed to parse response from create certificate [{str(ex)}]") from ex
        raise ArkServiceException(f'Failed to add a new certificate [{resp.text}] - [{resp.status_code}]')

    def certificate(self, get_certificate: ArkDPAGetCertificate) -> ArkDPACertificate:
        """
        Retrieves a certificate from the Access Certificates Service.

        Args:
            get_certificate (ArkDPAGetCertificate): The ID of the certificate to retrieve

        Raises:
            ArkServiceException: When the certificate could not be retrieved

        Returns:
            ArkDPACertificate: The retrieved certificate
        """
        self._logger.info(f'Retrieving certificate [{get_certificate.certificate_id}]')
        resp = self.__client.get(CERTIFICATE_API.format(certificate_id=get_certificate.certificate_id))
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to retrieve certificate [{get_certificate.certificate_id}] [{resp.text}]')
        try:
            return ArkDPACertificate.parse_obj(resp.json())
        except (ValidationError, JSONDecodeError) as ex:
            self._logger.exception(f'Failed to parse certificate response [{str(ex)}] - [{resp.text}]')
            raise ArkServiceException(f'Failed to parse policy response [{str(ex)}]') from ex

    def delete_certificate(self, cert: ArkDPADeleteCertificate) -> None:
        """
        Deletes an existing certificate.

        Args:
            cert (ArkDPADeleteCertificate): The ID of the certificate to delete

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f"Deleting certificate [{cert.certificate_id}]")
        resp: Response = self.__client.delete(CERTIFICATE_API.format(certificate_id=cert.certificate_id))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete certificate [{cert.certificate_id}] [{resp.status_code}]')

    def update_certificate(self, update_certificate: ArkDPAUpdateCertificate) -> None:
        """
        Updates an existing certificate.

        Args:
            update_certificate (ArkDPAUpdateCertificate): The ID of the certificate to update

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f"Updating certificate [{update_certificate.certificate_id}]")
        try:
            with open(update_certificate.file, 'r', encoding='utf-8') as f:
                cert_body = f.read()
        except Exception as ex:
            raise ArkServiceException(f'Failed to read certificate file [{update_certificate.file}] [{str(ex)}]') from ex
        if not cert_body:
            raise ArkServiceException(f'Certificate file [{update_certificate.file}] is empty')
        update_certificate_req = ArkDPAUpdateCertificateRequest(cert_body=cert_body, **update_certificate.dict()).dict()
        resp = self.__client.put(CERTIFICATE_API.format(certificate_id=update_certificate.certificate_id), json=update_certificate_req)
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to update the certificate [{resp.text}] - [{resp.status_code}]')

    def list_certificates(self) -> List[ArkDPAShortCertificate]:
        """
        Lists all certificates.

        Raises:
            ArkServiceException: _description_

        Returns:
            list[ArkDPACertificate]: _description_
        """
        self._logger.info("Listing certificates.")
        resp = self.__client.get(CERTIFICATES_API)
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to list certificates [{resp.text}] - [{resp.status_code}]')
        try:
            return [ArkDPAShortCertificate.parse_obj(cert) for cert in resp.json()['certificates']['items']]
        except (ValidationError, JSONDecodeError) as ex:
            self._logger.exception(f'Failed to parse certificate response [{str(ex)}] - [{resp.text}]')
            raise ArkServiceException(f'Failed to parse certificate response [{str(ex)}]') from ex

    def list_certificates_by(self, certificates_filter: ArkDPACertificatesFilter) -> List[ArkDPAShortCertificate]:
        """
        Lists certificates matching the specified filters.

        Args:
            certificates_filter (ArkDPACertificatesFilter): _description_

        Returns:
            List[ArkDPAShortCertificate]: _description_
        """
        self._logger.info(f'Retrieving certificates by filter [{certificates_filter}]')
        certs = self.list_certificates()

        if certificates_filter.domain_name:
            certs = [cert for cert in certs if certificates_filter.domain_name.lower() in cert.domain.lower()]

        if certificates_filter.cert_name:
            certs = [cert for cert in certs if certificates_filter.cert_name.lower() in cert.cert_name.lower()]

        return certs

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
