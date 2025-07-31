from base64 import b64encode
from fnmatch import fnmatch
from http import HTTPStatus
from pathlib import Path
from typing import Final, List, Optional, Set, Union

from overrides import overrides
from pydantic import TypeAdapter, ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.pcloud.platforms import (
    ArkPCloudActivateTargetPlatform,
    ArkPCloudDeactivateTargetPlatform,
    ArkPCloudDeleteTargetPlatform,
    ArkPCloudDuplicatedTargetPlatformInfo,
    ArkPCloudDuplicateTargetPlatform,
    ArkPCloudExportPlatform,
    ArkPCloudExportTargetPlatform,
    ArkPCloudGetPlatform,
    ArkPCloudGetTargetPlatform,
    ArkPCloudImportPlatform,
    ArkPCloudImportTargetPlatform,
    ArkPCloudPlatform,
    ArkPCloudPlatformDetails,
    ArkPCloudPlatformsFilter,
    ArkPCloudPlatformsStats,
    ArkPCloudPlatformType,
    ArkPCloudTargetPlatform,
    ArkPCloudTargetPlatformsFilter,
    ArkPCloudTargetPlatformsStats,
)
from ark_sdk_python.services.pcloud.common import ArkPCloudBaseService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='pcloud-platforms', required_authenticator_names=[], optional_authenticator_names=['isp']
)
PLATFORMS_URL: Final[str] = 'platforms'
PLATFORM_URL: Final[str] = 'platforms/{platform_id}'
IMPORT_PLATFORM_URL: Final[str] = 'platforms/import'
EXPORT_PLATFORM_URL: Final[str] = 'platforms/{platform_id}/export'
TARGET_PLATFORMS_URL: Final[str] = 'platforms/targets'
TARGET_PLATFORM_URL: Final[str] = 'platforms/targets/{target_platform_id}'
EXPORT_TARGET_PLATFORM_URL: Final[str] = 'platforms/targets/{target_platform_id}/export'
DUPLICATE_TARGET_PLATFORM_URL: Final[str] = 'platforms/targets/{target_platform_id}'
ACTIVATE_TARGET_PLATFORM_URL: Final[str] = 'platforms/targets/{target_platform_id}/activate'
DEACTIVATE_TARGET_PLATFORM_URL: Final[str] = 'platforms/targets/{target_platform_id}/deactivate'


class ArkPCloudPlatformsService(ArkPCloudBaseService):
    def __list_platforms_by_filters(
        self, active: Optional[bool] = None, platform_type: Optional[ArkPCloudPlatformType] = None, platform_name: Optional[str] = None
    ) -> List[ArkPCloudPlatform]:
        args = {}
        if active is not None:
            args['Active'] = active
        if platform_type:
            args['PlatformType'] = platform_type.value
        if platform_name:
            args['Search'] = platform_name
        resp: Response = self._client.get(PLATFORMS_URL, params=args)
        if resp.status_code == HTTPStatus.OK:
            try:
                data = resp.json()
                # Platform type may come in uppercase, lowercase it just in case
                for p in data['Platforms']:
                    p['general']['platformType'] = p['general']['platformType'].lower()
                return TypeAdapter(List[ArkPCloudPlatform]).validate_python(data['Platforms'])
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse list platforms response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse list platforms response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to list platforms [{resp.text}] - [{resp.status_code}]')

    def list_platforms(self) -> List[ArkPCloudPlatform]:
        """
        Lists all the platforms visible to the user
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/rest-api-get-platforms.htm

        Returns:
            List[ArkPCloudPlatform]: _description_
        """
        self._logger.info('Listing all platforms')
        return self.__list_platforms_by_filters()

    def list_platforms_by(self, platforms_filter: ArkPCloudPlatformsFilter) -> List[ArkPCloudPlatform]:
        """
        Lists platforms by given filters
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/rest-api-get-platforms.htm

        Args:
            platforms_filter (ArkPCloudPlatformsFilter): _description_

        Returns:
            List[ArkPCloudPlatform]: _description_
        """
        self._logger.info(f'Listing platforms by filter [{platforms_filter}]')
        return self.__list_platforms_by_filters(
            active=platforms_filter.active, platform_type=platforms_filter.platform_type, platform_name=platforms_filter.platform_name
        )

    def platform(self, get_platform: ArkPCloudGetPlatform) -> Union[ArkPCloudPlatform, ArkPCloudPlatformDetails]:
        """
        Retrieves a platform by id
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/GetPlatformDetails.htm

        Args:
            get_platform (ArkPCloudGetPlatform): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            Union[ArkPCloudPlatform, ArkPCloudPlatformDetails]: Platform details in appropriate format
        """
        self._logger.info(f'Retrieving platform [{get_platform.platform_id}]')
        resp: Response = self._client.get(PLATFORM_URL.format(platform_id=get_platform.platform_id))
        if resp.status_code == HTTPStatus.OK:
            try:
                # Try the old model first for backward compatibility
                return ArkPCloudPlatform.model_validate(resp.json())
            except ValidationError:
                try:
                    # Fallback to new Details API model
                    return ArkPCloudPlatformDetails.model_validate(resp.json())
                except (ValidationError, JSONDecodeError) as ex:
                    self._logger.exception(f'Failed to parse platform response [{str(ex)}] - [{resp.text}]')
                    raise ArkServiceException(f'Failed to parse platform response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve platform [{resp.text}] - [{resp.status_code}]')

    def import_platform(self, import_platform: ArkPCloudImportPlatform) -> ArkPCloudPlatform:
        """
        Tries to import a platform zip data
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PrivCloud-SS/Latest/en/Content/WebServices/ImportPlatform.htm

        Args:
            import_platform (ArkPCloudImportPlatform): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudPlatform: _description_
        """
        self._logger.info('Importing platform')
        platform_path = Path(import_platform.platform_zip_path)
        if not platform_path.exists():
            raise ArkServiceException(f'Given path [{str(platform_path)}] does not exist or is invalid')
        zip_data = b64encode(platform_path.read_bytes()).decode()
        resp: Response = self._client.post(IMPORT_PLATFORM_URL, json={'ImportFile': zip_data})
        if resp.status_code == HTTPStatus.CREATED:
            try:
                platform_id = resp.json()['PlatformID']
                return self.platform(ArkPCloudGetPlatform(platform_id=platform_id))
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse import platform response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse import platform response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to import platform [{resp.text}] - [{resp.status_code}]')

    def import_target_platform(self, import_platform: ArkPCloudImportTargetPlatform) -> ArkPCloudTargetPlatform:
        """
        Tries to import a platform zip data
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PrivCloud-SS/Latest/en/Content/WebServices/ImportPlatform.htm

        Args:
            import_platform (ArkPCloudImportTargetPlatform): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudTargetPlatform: _description_
        """
        self._logger.info('Importing target platform')
        platform_path = Path(import_platform.platform_zip_path)
        if not platform_path.exists():
            raise ArkServiceException(f'Given path [{str(platform_path)}] does not exist or is invalid')
        zip_data = b64encode(platform_path.read_bytes()).decode()
        resp: Response = self._client.post(IMPORT_PLATFORM_URL, json={'ImportFile': zip_data})
        if resp.status_code == HTTPStatus.CREATED:
            try:
                platform_id = resp.json()['PlatformID']
                platforms = self.list_target_platforms_by(ArkPCloudTargetPlatformsFilter(platform_id=platform_id))
                if platforms:
                    return platforms[0]
                raise ArkServiceException('Failed to find target platform after importing it')

            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse import platform response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse import platform response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to import platform [{resp.text}] - [{resp.status_code}]')

    def export_platform(self, export_platform: ArkPCloudExportPlatform) -> None:
        """
        Exports a platform zip data to a given folder by id
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PrivCloud-SS/Latest/en/Content/SDK/ExportPlatform.htm

        Args:
            export_platform (ArkPCloudExportPlatform): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Exporting platform [{export_platform.platform_id}] to folder [{export_platform.output_folder}]')
        output_folder = Path(export_platform.output_folder)
        output_folder.mkdir(exist_ok=True, parents=True)
        resp: Response = self._client.post(EXPORT_PLATFORM_URL.format(platform_id=export_platform.platform_id))
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to export platform [{resp.text}] - [{resp.status_code}]')
        (output_folder / export_platform.platform_id).write_bytes(resp.text.encode())

    def export_target_platform(self, export_platform: ArkPCloudExportTargetPlatform) -> None:
        """
        Exports a platform zip data to a given folder by id
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PrivCloud-SS/Latest/en/Content/SDK/ExportPlatform.htm

        Args:
            export_platform (ArkPCloudExportTargetPlatform): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Exporting platform [{export_platform.target_platform_id}] to folder [{export_platform.output_folder}]')
        output_folder = Path(export_platform.output_folder)
        output_folder.mkdir(exist_ok=True, parents=True)
        target_platform: ArkPCloudTargetPlatform = self.target_platform(
            ArkPCloudGetTargetPlatform(target_platform_id=export_platform.target_platform_id)
        )
        resp: Response = self._client.post(EXPORT_TARGET_PLATFORM_URL.format(target_platform_id=export_platform.target_platform_id))
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to export platform [{resp.text}] - [{resp.status_code}]')
        (output_folder / target_platform.platform_id).write_bytes(resp.text.encode())

    def platforms_stats(self) -> ArkPCloudPlatformsStats:
        """
        Calculates platforms stats

        Returns:
            ArkPCloudPlatformsStats: _description_
        """
        self._logger.info('Calculating platform statistics')
        platforms = self.list_platforms()
        platforms_stats = ArkPCloudPlatformsStats.model_construct()
        platforms_stats.platforms_count = len(platforms)

        # Get platforms per platform type
        platform_types: Set[ArkPCloudPlatformType] = {p.general.platform_type for p in platforms}
        platforms_stats.platforms_count_by_type = {
            pt: len([p for p in platforms if p.general.platform_type == pt]) for pt in platform_types
        }

        return platforms_stats

    def __list_target_platforms_by_filters(
        self,
        active: Optional[bool] = None,
        system_type: Optional[str] = None,
        periodic_verify: Optional[bool] = None,
        manual_verify: Optional[bool] = None,
        periodic_change: Optional[bool] = None,
        manual_change: Optional[bool] = None,
        automatic_reconcile: Optional[bool] = None,
        manual_reconcile: Optional[bool] = None,
    ) -> List[ArkPCloudTargetPlatform]:
        args = {}
        if active is not None:
            args['active'] = active
        if system_type is not None:
            args['systemType'] = system_type
        if periodic_verify is not None:
            args['periodicVerify'] = str(periodic_verify)
        if manual_verify is not None:
            args['manualVerify'] = str(manual_verify)
        if periodic_change is not None:
            args['periodicChange'] = str(periodic_change)
        if manual_change is not None:
            args['manualChange'] = str(manual_change)
        if automatic_reconcile is not None:
            args['automaticReconcile'] = str(automatic_reconcile)
        if manual_reconcile is not None:
            args['manualReconcile'] = str(manual_reconcile)
        params = " AND ".join([f"{k} eq {v}" for k, v in args.items()])
        resp: Response = self._client.get(TARGET_PLATFORMS_URL, params=params)
        if resp.status_code == HTTPStatus.OK:
            try:
                return TypeAdapter(List[ArkPCloudTargetPlatform]).validate_python(resp.json()['Platforms'])
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse list target platforms response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse list target platforms response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to list target platforms [{resp.text}] - [{resp.status_code}]')

    def list_target_platforms(self) -> List[ArkPCloudTargetPlatform]:
        """
        Lists all the target platforms visible to the user
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/rest-api-get-target-platforms.htm

        Returns:
            List[ArkPCloudTargetPlatform]: _description_
        """
        self._logger.info('Listing all target platforms')
        return self.__list_target_platforms_by_filters()

    def list_target_platforms_by(self, target_platforms_filter: ArkPCloudTargetPlatformsFilter) -> List[ArkPCloudTargetPlatform]:
        """
        Lists target platforms by given filters
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/rest-api-get-target-platforms.htm

        Args:
            target_platforms_filter (ArkPCloudTargetPlatformsFilter): _description_

        Returns:
            List[ArkPCloudTargetPlatform]: _description_
        """
        self._logger.info(f'Listing target platforms by filter [{target_platforms_filter}]')
        target_platforms = self.__list_target_platforms_by_filters(
            active=target_platforms_filter.active,
            system_type=target_platforms_filter.system_type,
            periodic_verify=target_platforms_filter.periodic_verify,
            manual_verify=target_platforms_filter.manual_verify,
            periodic_change=target_platforms_filter.periodic_change,
            manual_change=target_platforms_filter.manual_change,
            automatic_reconcile=target_platforms_filter.automatic_reconcile,
            manual_reconcile=target_platforms_filter.manual_reconcile,
        )

        # Filter by platform id
        if target_platforms_filter.platform_id:
            target_platforms = [p for p in target_platforms if fnmatch(p.platform_id.lower(), target_platforms_filter.platform_id.lower())]

        # Filter by name
        if target_platforms_filter.name:
            target_platforms = [p for p in target_platforms if fnmatch(p.name.lower(), target_platforms_filter.name.lower())]

        # Filter by active
        if target_platforms_filter.active is not None:
            target_platforms = [p for p in target_platforms if p.active is target_platforms_filter.active]

        return target_platforms

    def target_platform(self, get_target_platform: ArkPCloudGetTargetPlatform) -> ArkPCloudTargetPlatform:
        """
        Gets a target platform by id
        https://docs.cyberark.com/privilege-cloud-shared-services/Latest/en/Content/SDK/rest-api-get-target-platforms.htm

        Args:
            get_target_platform (ArkPCloudGetTargetPlatform): _description_

        Returns:
            ArkPCloudTargetPlatform: _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Retrieving target platform [{get_target_platform.target_platform_id}]')
        target_platform = [p for p in self.list_target_platforms() if p.id == get_target_platform.target_platform_id]
        if len(target_platform) != 1:
            raise ArkServiceException('Failed to get target platform')
        return target_platform[0]

    def activate_target_platform(self, activate_target_platform: ArkPCloudActivateTargetPlatform) -> None:
        """
        Activates a target platform by id
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PrivCloud-SS/Latest/en/Content/SDK/rest-api-activate-target-platform.htm

        Args:
            activate_target_platform (ArkPCloudActivateTargetPlatform): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Activating target platform [{activate_target_platform.target_platform_id}]')
        resp: Response = self._client.post(
            ACTIVATE_TARGET_PLATFORM_URL.format(target_platform_id=activate_target_platform.target_platform_id)
        )
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to activate target platform [{resp.text}] - [{resp.status_code}]')

    def deactivate_target_platform(self, deactivate_target_platform: ArkPCloudDeactivateTargetPlatform) -> None:
        """
        Deactivates a target platform by id
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PrivCloud-SS/Latest/en/Content/SDK/rest-api-deactivate-target-platform.htm

        Args:
            deactivate_target_platform (ArkPCloudDeactivateTargetPlatform): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Deactivating target platform [{deactivate_target_platform.target_platform_id}]')
        resp: Response = self._client.post(
            DEACTIVATE_TARGET_PLATFORM_URL.format(target_platform_id=deactivate_target_platform.target_platform_id)
        )
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to deactivate target platform [{resp.text}] - [{resp.status_code}]')

    def duplicate_target_platform(
        self, duplicate_target_platform: ArkPCloudDuplicateTargetPlatform
    ) -> ArkPCloudDuplicatedTargetPlatformInfo:
        """
        Duplicates a target platform by id
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/rest-api-duplicate-target-platforms.htm

        Args:
            duplicate_target_platform (ArkPCloudDuplicateTargetPlatform): _description_

        Returns:
            ArkPCloudDuplicatedTargetPlatformInfo: _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(
            f'Duplicates target platform [{duplicate_target_platform.target_platform_id}] to name [{duplicate_target_platform.name}]'
        )
        resp: Response = self._client.post(
            DUPLICATE_TARGET_PLATFORM_URL.format(target_platform_id=duplicate_target_platform.target_platform_id),
            json=duplicate_target_platform.model_dump(by_alias=True, exclude={'target_platform_id'}),
        )
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkPCloudDuplicatedTargetPlatformInfo.model_validate(resp.json())
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse duplicate target platform response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse duplicate target platform response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to duplicate target platform [{resp.text}] - [{resp.status_code}]')

    def delete_target_platform(self, delete_target_platform: ArkPCloudDeleteTargetPlatform) -> None:
        """
        Deletes a target platform by id
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/rest-api-delete-target-platform.htm

        Args:
            delete_target_platform (ArkPCloudDeleteTargetPlatform): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Deleting target platform [{delete_target_platform.target_platform_id}]')
        resp: Response = self._client.delete(TARGET_PLATFORM_URL.format(target_platform_id=delete_target_platform.target_platform_id))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete target platform [{resp.text}] - [{resp.status_code}]')

    def target_platforms_stats(self) -> ArkPCloudTargetPlatformsStats:
        """
        Calculates target platforms stats

        Returns:
            ArkPCloudTargetPlatformsStats: _description_
        """
        self._logger.info('Calculating target platform statistics')
        target_platforms = self.list_target_platforms()
        target_platforms_stats = ArkPCloudTargetPlatformsStats.model_construct()
        target_platforms_stats.target_platforms_count = len(target_platforms)

        # Get target platforms per system type
        target_platform_system_types: Set[str] = {p.system_type for p in target_platforms}
        target_platforms_stats.target_platforms_count_by_system_type = {
            pt: len([p for p in target_platforms if p.system_type == pt]) for pt in target_platform_system_types
        }

        return target_platforms_stats

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
