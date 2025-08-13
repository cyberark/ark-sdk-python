from fnmatch import fnmatch
from http import HTTPStatus
from typing import Final, List, Optional

from dateutil.parser import parse
from overrides import overrides
from pydantic import TypeAdapter
from requests import Response

from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.pcloud.applications import (
    ArkPCloudAddApplication,
    ArkPCloudAddApplicationAuthMethod,
    ArkPCloudAppicationsStats,
    ArkPCloudApplication,
    ArkPCloudApplicationAuthMethod,
    ArkPCloudApplicationAuthMethodsFilter,
    ArkPCloudApplicationAuthMethodType,
    ArkPCloudApplicationsFilter,
    ArkPCloudDeleteApplication,
    ArkPCloudDeleteApplicationAuthMethod,
    ArkPCloudGetApplication,
    ArkPCloudGetApplicationAuthMethod,
    ArkPCloudListApplicationAuthMethods,
)
from ark_sdk_python.services.pcloud.common import ArkPCloudBaseService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='pcloud-applications', required_authenticator_names=[], optional_authenticator_names=['isp']
)
BASE_APPLICATIONS_URL: Final[str] = 'PIMServices.svc/Applications'
BASE_APPLICATION_URL: Final[str] = 'PIMServices.svc/Applications/{app_id}'
BASE_AUTH_METHODS_URL: Final[str] = 'PIMServices.svc/Applications/{app_id}/Authentications'
BASE_AUTH_METHOD_URL: Final[str] = 'PIMServices.svc/Applications/{app_id}/Authentications/{auth_id}'


class ArkPCloudApplicationsService(ArkPCloudBaseService):
    def __init__(
        self,
        isp_auth: Optional[ArkISPAuth] = None,
    ) -> None:
        super().__init__(isp_auth, 'webservices')

    def add_application(self, add_application: ArkPCloudAddApplication) -> ArkPCloudApplication:
        """
        Adds a new application for CP / CCP
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PrivCloud/Latest/en/Content/WebServices/Add%20Application.htm

        Args:
            add_application (ArkPCloudAddApplication): _description_

        Returns:
            ArkPCloudApplication: _description_
        """
        self._logger.info(f'Adding new application with id [{add_application.app_id}]')
        try:
            parse(add_application.expiration_date)
        except Exception as ex:
            raise ArkServiceException('Expiration date format is invalid') from ex
        add_dict = add_application.model_dump(by_alias=True, exclude_none=True, exclude={'app_id'})
        add_dict['AppID'] = add_application.app_id
        resp: Response = self._client.post(BASE_APPLICATIONS_URL, json={'application': add_dict})
        if resp.status_code == HTTPStatus.CREATED:
            return self.application(ArkPCloudGetApplication(app_id=add_application.app_id))
        raise ArkServiceException(f'Failed to add application [{resp.text}] - [{resp.status_code}]')

    def delete_application(self, delete_application: ArkPCloudDeleteApplication) -> None:
        """
        Delete application by its id
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PrivCloud/Latest/en/Content/WebServices/Delete%20a%20Specific%20Application.htm

        Args:
            delete_application (ArkPCloudDeleteApplication): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Deleting application with id [{delete_application.app_id}]')
        resp: Response = self._client.delete(BASE_APPLICATION_URL.format(app_id=delete_application.app_id))
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to delete application [{resp.text}] - [{resp.status_code}]')

    def list_applications(self) -> List[ArkPCloudApplication]:
        """
        Lists all applications
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PrivCloud/Latest/en/Content/WebServices/List%20Applications.htm

        Returns:
            List[ArkPCloudApplication]: _description_
        """
        self._logger.info('Listing all applications')
        resp: Response = self._client.get(BASE_APPLICATIONS_URL)
        if resp.status_code == HTTPStatus.OK:
            return TypeAdapter(List[ArkPCloudApplication]).validate_python(resp.json()['application'])
        raise ArkServiceException(f'Failed to list applications [{resp.text}] - [{resp.status_code}]')

    def list_applications_by(self, applications_filter: ArkPCloudApplicationsFilter) -> List[ArkPCloudApplication]:
        """
        Lists applications by given filters
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PrivCloud/Latest/en/Content/WebServices/List%20Applications.htm

        Args:
            applications_filter (ArkPCloudApplicationsFilter): _description_

        Returns:
            List[ArkPCloudApplication]: _description_
        """
        self._logger.info(f'Listing applications by filters [{applications_filter}]')
        applications = self.list_applications()
        if applications_filter.location:
            applications = [a for a in applications if fnmatch(a.location, applications_filter.location)]
        if applications_filter.only_enabled:
            applications = [a for a in applications if not a.disabled]
        if applications_filter.business_owner_name:
            applications = [
                a
                for a in applications
                if fnmatch(a.business_owner_first_name, applications_filter.business_owner_name)
                or fnmatch(a.business_owner_first_name, applications_filter.business_owner_name)
            ]
        if applications_filter.business_owner_email:
            applications = [a for a in applications if a.business_owner_email == applications_filter.business_owner_email]
        return applications

    def application(self, get_application: ArkPCloudGetApplication) -> ArkPCloudApplication:
        """
        Retrieves an application by id
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PrivCloud/Latest/en/Content/WebServices/List%20a%20Specific%20Application.htm

        Args:
            get_application (ArkPCloudGetApplication): _description_

        Returns:
            ArkPCloudApplication: _description_
        """
        self._logger.info(f'Retrieving application by id [{get_application.app_id}]')
        resp: Response = self._client.get(BASE_APPLICATION_URL.format(app_id=get_application.app_id))
        if resp.status_code == HTTPStatus.OK:
            return ArkPCloudApplication.model_validate(resp.json()['application'])
        raise ArkServiceException(f'Failed to retrieve application [{resp.text}] - [{resp.status_code}]')

    def applications_stats(self) -> ArkPCloudAppicationsStats:
        """
        Calculates applications stats

        Returns:
            ArkPCloudAppicationsStats: _description_
        """
        self._logger.info('Calculating applications stats')
        applications = self.list_applications()
        applications_stats = ArkPCloudAppicationsStats.model_construct()
        applications_stats.count = len(applications)
        applications_stats.disabled_apps = [a.app_id for a in applications if a.disabled]
        apps_auth_types = {}
        for a in applications:
            auth_methods = self.list_application_auth_methods(ArkPCloudListApplicationAuthMethods(app_id=a.app_id))
            apps_auth_types[a.app_id] = [am.auth_type for am in auth_methods]
        applications_stats.applications_auth_method_types = apps_auth_types
        applications_stats.auth_types_count = {}
        for auth_method_types in apps_auth_types.values():
            for auth_method in auth_method_types:
                if auth_method not in applications_stats.auth_types_count:
                    applications_stats.auth_types_count[auth_method] = 0
                applications_stats.auth_types_count[auth_method] += 1
        return applications_stats

    def add_application_auth_method(self, add_application_auth_method: ArkPCloudAddApplicationAuthMethod) -> ArkPCloudApplicationAuthMethod:
        """
        Adds a new auth method for the application
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PrivCloud/Latest/en/Content/WebServices/Add%20Authentication.htm

        Args:
            add_application_auth_method (ArkPCloudAddApplicationAuthMethod): _description_

        Returns:
            ArkPCloudApplicationAuthMethod: _description_
        """
        self._logger.info(
            f'Adding a new auth method [{add_application_auth_method.auth_type}] for app [{add_application_auth_method.app_id}]'
        )
        auth_method_dict = None
        if add_application_auth_method.auth_type in [
            ArkPCloudApplicationAuthMethodType.Hash,
            ArkPCloudApplicationAuthMethodType.IP,
            ArkPCloudApplicationAuthMethodType.OsUser,
            ArkPCloudApplicationAuthMethodType.Path,
            ArkPCloudApplicationAuthMethodType.CertificateSerialNumber,
        ]:
            if not add_application_auth_method.auth_value:
                raise ArkServiceException('Auth value is required for the chosen auth method type')
            keys = {'auth_id', 'auth_type', 'auth_value', 'comment'}
            if add_application_auth_method.auth_type == ArkPCloudApplicationAuthMethodType.Path:
                keys = keys.union({'is_folder', 'allow_internal_scripts'})
            auth_method_dict = add_application_auth_method.model_dump(include=keys, by_alias=True, exclude_none=True)
        elif add_application_auth_method == ArkPCloudApplicationAuthMethodType.Certificate:
            if (
                not add_application_auth_method.subject
                and not add_application_auth_method.issuer
                and not add_application_auth_method.subject_alternative_name
            ):
                raise ArkServiceException('At least issuer, subject or san needs to be given for certificate auth type')
            auth_method_dict = add_application_auth_method.model_dump(
                include={'auth_id', 'auth_type', 'auth_value', 'subject', 'issuer', 'subject_alternative_name'},
                by_alias=True,
                exclude_none=True,
            )
        elif add_application_auth_method == ArkPCloudApplicationAuthMethodType.Kubernetes:
            if (
                not add_application_auth_method.namespace
                and not add_application_auth_method.image
                and not add_application_auth_method.env_var_name
                or not add_application_auth_method.env_var_value
            ):
                raise ArkServiceException('At least namespace, image, env var key and value needs to be given for kubernetes auth type')
            auth_method_dict = add_application_auth_method.model_dump(
                include={'auth_id', 'auth_type', 'auth_value', 'namespace', 'image', 'env_var_name', 'env_var_value'},
                by_alias=True,
                exclude_none=True,
            )
        else:
            raise ArkServiceException('Unsupported auth method type')
        resp: Response = self._client.post(
            BASE_AUTH_METHODS_URL.format(app_id=add_application_auth_method.app_id),
            json={
                'authentication': auth_method_dict,
            },
        )
        if resp.status_code == HTTPStatus.CREATED:
            return self.list_application_auth_methods_by(
                ArkPCloudApplicationAuthMethodsFilter(
                    app_id=add_application_auth_method.app_id, auth_types=[add_application_auth_method.auth_type]
                )
            )[0]
        raise ArkServiceException(f'Failed to add app auth method [{resp.text}] - [{resp.status_code}]')

    def delete_application_auth_method(self, delete_application_auth_method: ArkPCloudDeleteApplicationAuthMethod) -> None:
        """
        Deletes an auth method from an application
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PrivCloud/Latest/en/Content/WebServices/Delete%20a%20Specific%20Authentication.htm

        Args:
            delete_application_auth_method (ArkPCloudDeleteApplicationAuthMethod): _description_
        """
        self._logger.info(
            f'Deleting auth method from app [{delete_application_auth_method.app_id}] with id [{delete_application_auth_method.auth_id}]'
        )
        resp: Response = self._client.delete(
            BASE_AUTH_METHOD_URL.format(app_id=delete_application_auth_method.app_id, auth_id=delete_application_auth_method.auth_id)
        )
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to delete auth method [{resp.text}] - [{resp.status_code}]')

    def list_application_auth_methods(
        self, list_application_auth_methods: ArkPCloudListApplicationAuthMethods
    ) -> List[ArkPCloudApplicationAuthMethod]:
        """
        Lists all application auth methods
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PrivCloud/Latest/en/Content/WebServices/List%20all%20Authentication%20Methods%20of%20a%20Specific%20Application.htm

        Args:
            list_application_auth_methods (ArkPCloudListApplicationAuthMethods): _description_

        Returns:
            List[ArkPCloudApplicationAuthMethod]: _description_
        """
        self._logger.info(f'Listing all application [{list_application_auth_methods.app_id}]] auth methods')
        resp: Response = self._client.get(BASE_AUTH_METHODS_URL.format(app_id=list_application_auth_methods.app_id))
        if resp.status_code == HTTPStatus.OK:
            return TypeAdapter(List[ArkPCloudApplicationAuthMethod]).validate_python(resp.json()['authentication'])
        raise ArkServiceException(f'Failed to list application auth methods [{resp.text}] - [{resp.status_code}]]')

    def list_application_auth_methods_by(
        self, application_auth_methods_filter: ArkPCloudApplicationAuthMethodsFilter
    ) -> List[ArkPCloudApplicationAuthMethod]:
        """
        Lists application auth methods by given filters
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PrivCloud/Latest/en/Content/WebServices/List%20all%20Authentication%20Methods%20of%20a%20Specific%20Application.htm

        Args:
            application_auth_methods_filter (ArkPCloudApplicationAuthMethodsFilter): _description_

        Returns:
            List[ArkPCloudApplicationAuthMethod]: _description_
        """
        self._logger.info(f'Listing auth methods of app filtered [{application_auth_methods_filter}]')
        auth_methods = self.list_application_auth_methods(
            ArkPCloudListApplicationAuthMethods(app_id=application_auth_methods_filter.app_id)
        )
        if application_auth_methods_filter.auth_types:
            auth_methods = [a for a in auth_methods if a.auth_type in application_auth_methods_filter.auth_types]
        return auth_methods

    def application_auth_method(self, get_application_auth_method: ArkPCloudGetApplicationAuthMethod) -> ArkPCloudApplicationAuthMethod:
        """
        Retrives an auth method by app id and auth id

        Args:
            get_application_auth_method (ArkPCloudGetApplicationAuthMethod): _description_

        Returns:
            ArkPCloudApplicationAuthMethod: _description_
        """
        self._logger.info(
            f'Retrieving auth method of app [{get_application_auth_method.app_id}] and id [{get_application_auth_method.auth_id}]'
        )
        auth_methods = [
            a
            for a in self.list_application_auth_methods(ArkPCloudListApplicationAuthMethods(app_id=get_application_auth_method.app_id))
            if a.auth_id == get_application_auth_method.auth_id
        ]
        if not auth_methods:
            raise ArkServiceException('Failed to find auth method')
        return auth_methods[0]

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
