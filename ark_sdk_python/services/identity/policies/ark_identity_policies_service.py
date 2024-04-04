from http import HTTPStatus
from typing import Final, List

from overrides import overrides
from pydantic import parse_obj_as
from pydantic.error_wrappers import ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.models.ark_exceptions import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.identity.policies import (
    ArkIdentityAddAuthenticationProfile,
    ArkIdentityAddPolicy,
    ArkIdentityAuthenticationProfile,
    ArkIdentityDisablePolicy,
    ArkIdentityEnablePolicy,
    ArkIdentityGetAuthenticationProfile,
    ArkIdentityGetPolicy,
    ArkIdentityPolicy,
    ArkIdentityPolicyInfo,
    ArkIdentityPolicyOperation,
    ArkIdentityPolicyOperationType,
    ArkIdentityRemoveAuthenticationProfile,
    ArkIdentityRemovePolicy,
)
from ark_sdk_python.models.services.identity.roles import ArkIdentityRoleIdByName
from ark_sdk_python.services.identity.common import ArkIdentityBaseService
from ark_sdk_python.services.identity.roles import ArkIdentityRolesService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='identity-policies', required_authenticator_names=['isp'], optional_authenticator_names=[]
)

SAVE_PROFILE_URL: Final[str] = 'AuthProfile/SaveProfile'
DELETE_PROFILE_URL: Final[str] = 'AuthProfile/DeleteProfile'
GET_PROFILES_URL: Final[str] = 'AuthProfile/GetDecoratedProfileList'
SAVE_POLICY_URL: Final[str] = 'Policy/SavePolicyBlock3'
DELETE_POLICY_URL: Final[str] = 'Policy/DeletePolicyBlock'
LIST_POLICIES_URL: Final[str] = 'Policy/GetNicePlinks'
GET_POLICY_URL: Final[str] = 'Policy/GetPolicyBlock'


class ArkIdentityPoliciesService(ArkIdentityBaseService):
    def add_authentication_profile(
        self, add_authentication_profile: ArkIdentityAddAuthenticationProfile
    ) -> ArkIdentityAuthenticationProfile:
        """
        Adds a new authentication profile

        Args:
            add_authentication_profile (ArkIdentityAddAuthenticationProfile): _description_

        Returns:
            ArkIdentityAuthenticationProfile: _description_
        """
        self._logger.info(f'Adding authentication profile [{add_authentication_profile.auth_profile_name}]')
        data = {
            'settings': {
                'Name': add_authentication_profile.auth_profile_name,
                'Challenges': [','.join(add_authentication_profile.first_challenges)],
                'DurationInMinutes': add_authentication_profile.duration_in_minutes,
            }
        }
        if add_authentication_profile.second_challenges:
            data['settings']['Challenges'].append(','.join(add_authentication_profile.second_challenges))
        if add_authentication_profile.additional_data:
            data['settings']['AdditionalData'] = add_authentication_profile.additional_data
        response: Response = self._client.post(f'{self._url_prefix}{SAVE_PROFILE_URL}', json=data)
        try:
            result = response.json()
            if response.status_code != HTTPStatus.OK or not result['success']:
                raise ArkServiceException(f'Failed to add authentication profile [{response.text}] - [{response.status_code}]')
            return ArkIdentityAuthenticationProfile.parse_obj(result['Result'])
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse add authentication profile response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse add authentication profile response [{str(ex)}]') from ex

    def remove_authentication_profile(self, remove_authentication_profile: ArkIdentityRemoveAuthenticationProfile) -> None:
        """
        Removes an authentication profile by name or id

        Args:
            remove_authentication_profile (ArkIdentityRemoveAuthenticationProfile): _description_
        """
        if remove_authentication_profile.auth_profile_name and not remove_authentication_profile.auth_profile_id:
            remove_authentication_profile.auth_profile_id = self.authentication_profile(
                ArkIdentityGetAuthenticationProfile(auth_profile_name=remove_authentication_profile.auth_profile_name)
            ).uuid
        self._logger.info(f'Removing authentication profile [{remove_authentication_profile.auth_profile_id}]')
        response: Response = self._client.post(
            f'{self._url_prefix}{DELETE_PROFILE_URL}', json={'uuid': remove_authentication_profile.auth_profile_id}
        )
        try:
            if response.status_code != HTTPStatus.OK or not response.json()['success']:
                raise ArkServiceException(f'Failed to remove authentication profile [{response.text}] - [{response.status_code}]')
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse remove authentication profile response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse remove authentication profile response [{str(ex)}]') from ex

    def list_authentication_profiles(self) -> List[ArkIdentityAuthenticationProfile]:
        """
        List available authentication profiles

        Raises:
            ArkServiceException: _description_

        Returns:
            List[ArkIdentityAuthenticationProfile]: _description_
        """
        self._logger.info('Listing authentication profiles')
        response: Response = self._client.post(f'{self._url_prefix}{GET_PROFILES_URL}')
        try:
            result = response.json()
            if response.status_code != HTTPStatus.OK or not result['success']:
                raise ArkServiceException(f'Failed to list authentication profiles [{response.text}] - [{response.status_code}]')
            return parse_obj_as(List[ArkIdentityAuthenticationProfile], [r['Row'] for r in result['Result']['Results']])
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse list authentication profiles response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse list authentication profiles response [{str(ex)}]') from ex

    def authentication_profile(self, get_authentication_profile: ArkIdentityGetAuthenticationProfile) -> ArkIdentityAuthenticationProfile:
        """
        Retrieve an authentication profile by id or name

        Args:
            get_authentication_profile (ArkIdentityGetAuthenticationProfile): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkIdentityAuthenticationProfile: _description_
        """
        self._logger.info('Retrieving authentication profile')
        auth_profiles = self.list_authentication_profiles()
        if get_authentication_profile.auth_profile_id:
            auth_profiles = [p for p in auth_profiles if p.uuid == get_authentication_profile.auth_profile_id]
        if get_authentication_profile.auth_profile_name:
            auth_profiles = [p for p in auth_profiles if p.name == get_authentication_profile.auth_profile_name]
        if len(auth_profiles) == 0:
            raise ArkServiceException('Failed to find authentication profile')
        return auth_profiles[0]

    def add_policy(self, add_policy: ArkIdentityAddPolicy) -> ArkIdentityPolicy:
        """
        Adds a new policy

        Args:
            add_policy (ArkIdentityAddPolicy): _description_

        Returns:
            ArkIdentityPolicy: _description_
        """
        self._logger.info(f'Adding policy [{add_policy.policy_name}]')
        roles_service = ArkIdentityRolesService(self._isp_auth)
        policies_list = [p.dict(by_alias=True) for p in self.list_policies()]
        policy_name = f'/Policy/{add_policy.policy_name}'
        policy_link = {
            "Description": add_policy.description,
            "PolicySet": policy_name,
            "LinkType": "Role",
            "Priority": 1,
            "Params": [roles_service.role_id_by_name(ArkIdentityRoleIdByName(role_name=role_name)) for role_name in add_policy.role_names],
            "Filters": [],
            "Allowedpolicies": [],
        }
        policies_list.insert(0, policy_link)
        data = {
            "plinks": policies_list,
            "policy": {
                "Path": policy_name,
                "Version": 1,
                "Description": add_policy.description,
                "Settings": {
                    "AuthenticationEnabled": 'true',
                    "/Core/Authentication/AuthenticationRulesDefaultProfileId": self.authentication_profile(
                        ArkIdentityGetAuthenticationProfile(auth_profile_name=add_policy.auth_profile_name)
                    ).uuid,
                    "/Core/Authentication/CookieAllowPersist": 'false',
                    "/Core/Authentication/AuthSessionMaxConcurrent": 0,
                    "/Core/Authentication/AllowIwa": 'true',
                    "/Core/Authentication/IwaSetKnownEndpoint": 'false',
                    "/Core/Authentication/IwaSatisfiesAllMechs": 'false',
                    "/Core/Authentication/AllowZso": 'true',
                    "/Core/Authentication/ZsoSkipChallenge": 'true',
                    "/Core/Authentication/ZsoSetKnownEndpoint": 'false',
                    "/Core/Authentication/ZsoSatisfiesAllMechs": 'false',
                    "/Core/Authentication/NoMfaMechLogin": 'false',
                    "/Core/Authentication/FederatedLoginAllowsMfa": 'false',
                    "/Core/Authentication/FederatedLoginSatisfiesAllMechs": 'false',
                    "/Core/MfaRestrictions/BlockMobileMechsOnMobileLogin": 'false',
                    "/Core/Authentication/ContinueFailedSessions": 'true',
                    "/Core/Authentication/SkipMechsInFalseAdvance": 'true',
                    "/Core/Authentication/AllowLoginMfaCache": 'false',
                },
                "Newpolicy": 'true',
            },
        }
        if add_policy.settings:
            data['policy']['Settings'].update(add_policy.settings)
        response: Response = self._client.post(f'{self._url_prefix}{SAVE_POLICY_URL}', json=data)
        try:
            if response.status_code != HTTPStatus.OK or not response.json()['success']:
                raise ArkServiceException(f'Failed to add policy [{response.text}] - [{response.status_code}]')
            return self.policy(ArkIdentityGetPolicy(policy_name=add_policy.policy_name))
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse add policy response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse add policy response [{str(ex)}]') from ex

    def disable_default_policy(self) -> None:
        """
        Disables the default policy (makes it inactive)
        """
        self.disable_policy(
            disable_policy=ArkIdentityDisablePolicy(
                policy_name='/Policy/Default Policy',
            ),
        )

    def enable_default_policy(self) -> None:
        """
        Enables the default policy (makes it active)
        """
        self.enable_policy(
            enable_policy=ArkIdentityEnablePolicy(
                policy_name='/Policy/Default Policy',
            ),
        )

    def perform_action_on_policy(self, policy_operation: ArkIdentityPolicyOperation) -> None:
        """
        Performs operation on policy (enable/disable)

        Args:
            policy_operation (ArkIdentityPolicyOperation): _description_

        Raises:
            ArkServiceException: _description_
        """
        policy_name = policy_operation.policy_name
        policy = self.policy(get_policy=ArkIdentityGetPolicy(policy_name=policy_name))

        policies_list = [p.dict(by_alias=True) for p in self.list_policies()]
        for elem in policies_list:
            if elem['ID'] == policy_name:
                elem['LinkType'] = policy_operation.operation_type.value
        data = {
            "plinks": policies_list,
            "policy": {
                "Path": policy_name,
                "Version": 1,
                "Description": policy.description,
                "RevStamp": policy.rev_stamp,
                "Settings": policy.settings,
                "Newpolicy": False,
            },
        }
        response: Response = self._client.post(f'{self._url_prefix}{SAVE_POLICY_URL}', json=data)
        try:
            if response.status_code != HTTPStatus.OK or not response.json()['success']:
                raise ArkServiceException(f'Failed to add policy [{response.text}] - [{response.status_code}]')
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse perform policy action response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse perform policy action response [{str(ex)}]') from ex

    def enable_policy(self, enable_policy: ArkIdentityEnablePolicy) -> None:
        """
        Enables a policy by name

        Args:
            enable_policy (ArkIdentityEnablePolicy): _description_

        """
        self._logger.info(f'Making Policy [{enable_policy.policy_name}] active')
        self.perform_action_on_policy(
            policy_operation=ArkIdentityPolicyOperation(
                policy_name=enable_policy.policy_name,
                operation_type=ArkIdentityPolicyOperationType.ENABLE,
            ),
        )

    def disable_policy(self, disable_policy: ArkIdentityDisablePolicy) -> None:
        """
        Disables a policy by name

        Args:
            disable_policy (ArkIdentityDisablePolicy): _description_

        """
        self._logger.info(f'Making Policy [{disable_policy.policy_name}] inactive')
        self.perform_action_on_policy(
            policy_operation=ArkIdentityPolicyOperation(
                policy_name=disable_policy.policy_name,
                operation_type=ArkIdentityPolicyOperationType.DISABLE,
            ),
        )

    def remove_policy(self, remove_policy: ArkIdentityRemovePolicy) -> None:
        """
        Removes a policy by name

        Args:
            remove_policy (ArkIdentityRemovePolicy): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Removing policy [{remove_policy.policy_name}]')
        policy_name = remove_policy.policy_name
        if not policy_name.startswith('/Policy/'):
            policy_name = f'/Policy/{policy_name}'
        response: Response = self._client.post(f'{self._url_prefix}{DELETE_POLICY_URL}', json={'path': policy_name})
        try:
            if response.status_code != HTTPStatus.OK or not response.json()['success']:
                raise ArkServiceException(f'Failed to remove policy [{response.text}] - [{response.status_code}]')
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse remove policy response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse remove policy response [{str(ex)}]') from ex

    def list_policies(self) -> List[ArkIdentityPolicyInfo]:
        """
        Lists all policies short info

        Returns:
            List[ArkIdentityPolicyInfo]: _description_
        """
        self._logger.info('Listing all policies')
        response: Response = self._client.post(f'{self._url_prefix}{LIST_POLICIES_URL}')
        try:
            result = response.json()
            if response.status_code != HTTPStatus.OK or not result['success']:
                raise ArkServiceException(f'Failed to list policies [{response.text}] - [{response.status_code}]')
            return parse_obj_as(List[ArkIdentityPolicyInfo], [p['Row'] for p in result['Result']['Results']])
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse list policies response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse list policies response [{str(ex)}]') from ex

    def policy(self, get_policy: ArkIdentityGetPolicy) -> ArkIdentityPolicy:
        """
        Retrieves a policy full info by name

        Args:
            get_policy (ArkIdentityGetPolicy): _description_

        Returns:
            ArkIdentityPolicy: _description_
        """
        self._logger.info(f'Retrieving policy [{get_policy.policy_name}]')
        policy_name = get_policy.policy_name
        if not policy_name.startswith('/Policy/'):
            policy_name = f'/Policy/{policy_name}'
        response: Response = self._client.post(f'{self._url_prefix}{GET_POLICY_URL}', json={'name': policy_name})
        try:
            result = response.json()
            if response.status_code != HTTPStatus.OK or not result['success']:
                raise ArkServiceException(f'Failed to list policies [{response.text}] - [{response.status_code}]')
            return ArkIdentityPolicy.parse_obj(result['Result'])
        except (ValidationError, JSONDecodeError, KeyError) as ex:
            self._logger.exception(f'Failed to parse policy response [{str(ex)}] - [{response.text}]')
            raise ArkServiceException(f'Failed to parse policy response [{str(ex)}]') from ex

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
