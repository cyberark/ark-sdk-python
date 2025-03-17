import itertools
from http import HTTPStatus
from typing import Final, Iterator, List, Optional, Set
from urllib.parse import parse_qs, urlparse

from overrides import overrides
from pydantic import TypeAdapter, ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.common import ArkPage
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.pcloud.accounts import (
    ArkPCloudAccount,
    ArkPCloudAccountCredentials,
    ArkPCloudAccountSecretVersion,
    ArkPCloudAccountsFilter,
    ArkPCloudAccountsStats,
    ArkPCloudAddAccount,
    ArkPCloudChangeAccountCredentials,
    ArkPCloudDeleteAccount,
    ArkPCloudGenerateAccountCredentials,
    ArkPCloudGetAccount,
    ArkPCloudGetAccountCredentials,
    ArkPCloudLinkAccount,
    ArkPCloudListAccountSecretVersions,
    ArkPCloudReconcileAccountCredentials,
    ArkPCloudSetAccountNextCredentials,
    ArkPCloudUnlinkAccount,
    ArkPCloudUpdateAccount,
    ArkPCloudUpdateAccountCredentialsInVault,
    ArkPCloudVerifyAccountCredentials,
)
from ark_sdk_python.services.pcloud.common import ArkPCloudBaseService

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='pcloud-accounts', required_authenticator_names=[], optional_authenticator_names=['isp']
)
ACCOUNTS_URL: Final[str] = 'accounts'
ACCOUNT_URL: Final[str] = 'accounts/{account_id}'
ACCOUNT_SECRET_VERSIONS: Final[str] = 'accounts/{account_id}/secret/versions'
GENERATE_ACCOUNT_CREDENTIALS: Final[str] = 'accounts/{account_id}/secret/generate'
VERIFY_ACCOUNT_CREDENTIALS: Final[str] = 'accounts/{account_id}/verify'
CHANGE_ACCOUNT_CREDENTIALS: Final[str] = 'accounts/{account_id}/change'
SET_ACCOUNT_NEXT_CREDENTIALS: Final[str] = 'accounts/{account_id}/setnextpassword'
UPDATE_ACCOUNT_CREDENTIALS_IN_VAULT: Final[str] = 'accounts/{account_id}/password/update'
RETRIEVE_ACCOUNT_CREDENTIALS: Final[str] = 'accounts/{account_id}/password/retrieve'
RECONCILE_ACCOUNT_CREDENTIALS: Final[str] = 'accounts/{account_id}/reconcile'
LINK_ACCOUNT: Final[str] = 'accounts/{account_id}/linkaccount'
UNLINK_ACCOUNT: Final[str] = 'accounts/{account_id}/linkaccount/{extra_password_index}'

ArkPCloudAccountsPage = ArkPage[ArkPCloudAccount]


class ArkPCloudAccountsService(ArkPCloudBaseService):
    def __list_accounts_with_filters(
        self,
        search: Optional[str] = None,
        search_type: Optional[str] = None,
        sort: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        safe_name: Optional[str] = None,
    ) -> Iterator[ArkPCloudAccountsPage]:
        query = {}
        if search:
            query['search'] = search
        if search_type:
            query['searchType'] = search_type
        if sort:
            query['sort'] = sort
        if offset:
            query['offset'] = offset
        if limit:
            query['limit'] = limit
        if safe_name:
            query['filter'] = f'safeName eq {safe_name}'
        while True:
            resp: Response = self._client.get(ACCOUNTS_URL, params=query)
            if resp.status_code == HTTPStatus.OK:
                try:
                    result = resp.json()
                    accounts = TypeAdapter(List[ArkPCloudAccount]).validate_python(result['value'])
                    yield ArkPCloudAccountsPage(items=accounts)
                    if 'nextLink' in result:
                        query = parse_qs(urlparse(result['nextLink']).query)
                    else:
                        break
                except (ValidationError, JSONDecodeError, KeyError) as ex:
                    self._logger.exception(f'Failed to parse list accounts response [{str(ex)}] - [{resp.text}]')
                    raise ArkServiceException(f'Failed to parse list accounts response [{str(ex)}]') from ex
            else:
                raise ArkServiceException(f'Failed to list accounts [{resp.text}] - [{resp.status_code}]')

    def list_accounts(self) -> Iterator[ArkPCloudAccountsPage]:
        """
        Yields all visible accounts to the logged in user as pages of accounts
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/GetAccounts.htm

        Yields:
            Iterator[ArkPCloudAccountsPage]: _description_
        """
        self._logger.info('Listing all accounts')
        yield from self.__list_accounts_with_filters()

    def list_accounts_by(self, accounts_filter: ArkPCloudAccountsFilter) -> Iterator[ArkPCloudAccountsPage]:
        """
        Yields visible accounts to the logged in user by filters as pages of accounts
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/GetAccounts.htm

        Args:
            accounts_filter (ArkPCloudAccountsFilter): _description_

        Yields:
            Iterator[ArkPCloudAccountsPage]: _description_
        """
        self._logger.info(f'Listing accounts by filters [{accounts_filter}]')
        yield from self.__list_accounts_with_filters(
            accounts_filter.search,
            accounts_filter.search_type,
            accounts_filter.sort,
            accounts_filter.offset,
            accounts_filter.limit,
            accounts_filter.safe_name,
        )

    def list_account_secret_versions(
        self, list_account_secret_versions: ArkPCloudListAccountSecretVersions
    ) -> List[ArkPCloudAccountSecretVersion]:
        """
        Lists the given account secret versions
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/Secrets-Get-versions.htm

        Args:
            list_account_secret_versions (ArkPCloudListAccountSecretVersions): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            List[ArkPCloudAccountSecretVersion]: _description_
        """
        self._logger.info(f'Listing account [{list_account_secret_versions.account_id}] secret versions')
        resp: Response = self._client.get(ACCOUNT_SECRET_VERSIONS.format(account_id=list_account_secret_versions.account_id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return TypeAdapter(List[ArkPCloudAccountSecretVersion]).validate_python(resp.json()['versions'])
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse list account secret versions response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse list account secret versions response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to list account secret versions [{resp.text}] - [{resp.status_code}]')

    def generate_account_credentials(
        self, generate_account_credentials: ArkPCloudGenerateAccountCredentials
    ) -> ArkPCloudAccountCredentials:
        """
        Generate a new random password for an existing account with policy restrictions
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/Secrets-Generate-Password.htm

        Args:
            generate_account_credentials (ArkPCloudGenerateAccountCredentials): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudAccountCredentials: _description_
        """
        self._logger.info(f'Generating new password for account [{generate_account_credentials.account_id}]')
        resp: Response = self._client.post(GENERATE_ACCOUNT_CREDENTIALS.format(account_id=generate_account_credentials.account_id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkPCloudAccountCredentials(account_id=generate_account_credentials.account_id, password=resp.json()['password'])
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse genereate account credentials response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse genereate account credentials response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to generate password for account [{resp.text}] - [{resp.status_code}]')

    def verify_account_credentials(self, verify_account_credentials: ArkPCloudVerifyAccountCredentials) -> None:
        """
        Marks the account for password verification by CPM
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/Verify-credentials-v9-10.htm

        Args:
            verify_account_credentials (ArkPCloudVerifyAccountCredentials): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Marking account [{verify_account_credentials.account_id}] for verification')
        resp: Response = self._client.post(VERIFY_ACCOUNT_CREDENTIALS.format(account_id=verify_account_credentials.account_id))
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to mark account for password verification [{resp.text}] - [{resp.status_code}]')

    def change_account_credentials(self, change_account_credentials: ArkPCloudChangeAccountCredentials) -> None:
        """
        Marks the account for password changing immediately by CPM
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/Change-credentials-immediately.htm

        Args:
            change_account_credentials (ArkPCloudChangeAccountCredentials): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Marking account [{change_account_credentials.account_id}] for changing credentials immediately')
        resp: Response = self._client.post(CHANGE_ACCOUNT_CREDENTIALS.format(account_id=change_account_credentials.account_id))
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to mark account for changing credentials immediately [{resp.text}] - [{resp.status_code}]')

    def set_account_next_credentials(self, set_account_next_credentials: ArkPCloudSetAccountNextCredentials) -> None:
        """
        Marks the account to have its password changed to the given one via CPM
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/SetNextPassword.htm

        Args:
            set_account_next_credentials (ArkPCloudSetAccountNextCredentials): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Marking account [{set_account_next_credentials.account_id}] for changing credentials for the given password')
        resp: Response = self._client.post(
            SET_ACCOUNT_NEXT_CREDENTIALS.format(account_id=set_account_next_credentials.account_id),
            json=set_account_next_credentials.model_dump(exclude={'account_id'}, by_alias=True),
        )
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to mark account for changing credentials next password [{resp.text}] - [{resp.status_code}]')

    def update_account_credentials_in_vault(self, update_account_credentials_in_vault: ArkPCloudUpdateAccountCredentialsInVault) -> None:
        """
        Updates the account credentials only in the vault without changing it on the machine itself
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/ChangeCredentialsInVault.htm

        Args:
            update_account_credentials_in_vault (ArkPCloudUpdateAccountCredentialsInVault): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Updates account [{update_account_credentials_in_vault.account_id}] vault credentials')
        resp: Response = self._client.post(
            UPDATE_ACCOUNT_CREDENTIALS_IN_VAULT.format(account_id=update_account_credentials_in_vault.account_id),
            json=update_account_credentials_in_vault.model_dump(exclude={'account_id'}, by_alias=True),
        )
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to update credentials in vault for account [{resp.text}] - [{resp.status_code}]')

    def reconcile_account_credentials(self, reconcile_account_credentials: ArkPCloudReconcileAccountCredentials) -> None:
        """
        Marks the account for reconcilation
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/Reconcile-account.htm

        Args:
            reconcile_account_credentials (ArkPCloudReconcileAccountCredentials): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Marking account [{reconcile_account_credentials.account_id}] for reconcilation')
        resp: Response = self._client.post(RECONCILE_ACCOUNT_CREDENTIALS.format(account_id=reconcile_account_credentials.account_id))
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to reconcile account credentials [{resp.text}] - [{resp.status_code}]')

    def account(self, get_account: ArkPCloudGetAccount) -> ArkPCloudAccount:
        """
        Retrieves the account by id
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/Get%20Account%20Details.htm?

        Args:
            get_account (ArkPCloudGetAccount): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudAccount: _description_
        """
        self._logger.info(f'Retrieving account by id [{get_account.account_id}]')
        resp: Response = self._client.get(ACCOUNT_URL.format(account_id=get_account.account_id))
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkPCloudAccount.model_validate(resp.json())
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse account response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse account response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to retrieve account [{resp.text}] - [{resp.status_code}]')

    def account_credentials(self, get_account_credentials: ArkPCloudGetAccountCredentials) -> ArkPCloudAccountCredentials:
        """
        Retrieves the account credentials
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/GetPasswordValueV10.htm?

        Args:
            get_account_credentials (ArkPCloudGetAccountCredentials): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudAccountCredentials: _description_
        """
        self._logger.info(f'Retrieving account password for details [{get_account_credentials}]')
        body = {
            k.replace('_', '').title(): v
            for k, v in get_account_credentials.model_dump(exclude={'account_id', 'reason'}, exclude_none=True).items()
        }
        if get_account_credentials.reason:
            body['reason'] = get_account_credentials.reason
        resp: Response = self._client.post(RETRIEVE_ACCOUNT_CREDENTIALS.format(account_id=get_account_credentials.account_id), json=body)
        if resp.status_code == HTTPStatus.OK:
            return ArkPCloudAccountCredentials(
                account_id=get_account_credentials.account_id, password=resp.text[1:-1]  # Remove leading and trailing quotes
            )
        raise ArkServiceException(f'Failed to retrieve account credentials [{resp.text}] - [{resp.status_code}]')

    def add_account(self, add_account: ArkPCloudAddAccount) -> ArkPCloudAccount:
        """
        Adds a new account with given details
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/Add%20Account%20v10.htm?

        Args:
            add_account (ArkPCloudAddAccount): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudAccount: _description_
        """
        self._logger.info('Adding new account')
        if add_account.remote_machines_access:
            if (
                add_account.remote_machines_access.access_restricted_to_remote_machines
                and not add_account.remote_machines_access.remote_machines
            ):
                add_account.remote_machines_access = None
            elif not add_account.remote_machines_access.access_restricted_to_remote_machines:
                add_account.remote_machines_access.remote_machines = None

            elif add_account.remote_machines_access.remote_machines:
                add_account.remote_machines_access.remote_machines = ','.join(add_account.remote_machines_access.remote_machines)

        resp: Response = self._client.post(
            ACCOUNTS_URL, json=add_account.model_dump(by_alias=True, exclude_none=True, exclude_defaults=True)
        )
        if resp.status_code == HTTPStatus.CREATED:
            try:
                return ArkPCloudAccount.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse add account response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse add account response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to add account [{resp.text}] - [{resp.status_code}]')

    def update_account(self, update_account: ArkPCloudUpdateAccount) -> ArkPCloudAccount:
        """
        Updates an existing account with new details
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/SDK/UpdateAccount%20v10.htm

        Args:
            update_account (ArkPCloudUpdateAccount): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkPCloudAccount: _description_
        """
        self._logger.info(f'Updating account [{update_account.account_id}]')
        if update_account.remote_machines_access and not update_account.remote_machines_access.remote_machines:
            update_account.remote_machines_access = None
        operations = []
        for key, val in update_account.model_dump(exclude={'account_id'}, exclude_none=True, by_alias=True, exclude_defaults=True).items():
            operations.append({'op': 'replace', 'path': f'/{key}', 'value': val})
        resp: Response = self._client.patch(ACCOUNT_URL.format(account_id=update_account.account_id), json=operations)
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkPCloudAccount.model_validate(resp.json())
            except (ValidationError, JSONDecodeError) as ex:
                self._logger.exception(f'Failed to parse update account response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse update account response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to update account [{resp.text}] - [{resp.status_code}]')

    def delete_account(self, delete_account: ArkPCloudDeleteAccount) -> None:
        """
        Deletes an account by given id
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/Delete%20Account.htm

        Args:
            delete_account (ArkPCloudDeleteAccount): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Deleting account [{delete_account.account_id}]')
        resp: Response = self._client.delete(ACCOUNT_URL.format(account_id=delete_account.account_id))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise ArkServiceException(f'Failed to delete account [{resp.text}] - [{resp.status_code}]')

    def link_account(self, link_account: ArkPCloudLinkAccount) -> None:
        """
        Link an account by given info
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PrivCloud-SS/Latest/en/Content/WebServices/Link-account.htm

        Args:
            link_account (ArkPCloudLinkAccount): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(
            f'Linking account [{link_account.account_id}] '
            f'to name [{link_account.name}] in safe [{link_account.safe}] in folder [{link_account.folder}] '
            f'by idx [{link_account.extra_password_index}]'
        )
        resp: Response = self._client.post(
            LINK_ACCOUNT.format(account_id=link_account.account_id), json=link_account.model_dump(exclude={'account_id'}, by_alias=True)
        )
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to link account [{resp.text}] - [{resp.status_code}]')

    def unlink_account(self, unlink_account: ArkPCloudUnlinkAccount) -> None:
        """
        Link an account by given info
        https://docs.cyberark.com/Product-Doc/OnlineHelp/PrivCloud-SS/Latest/en/Content/WebServices/Link-account-unlink.htm

        Args:
            unlink_account (ArkPCloudUnlinkAccount): _description_

        Raises:
            ArkServiceException: _description_
        """
        self._logger.info(f'Unlinking account [{unlink_account.account_id}] by idx [{unlink_account.extra_password_index}]')
        resp: Response = self._client.delete(
            UNLINK_ACCOUNT.format(account_id=unlink_account.account_id, extra_password_index=unlink_account.extra_password_index)
        )
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to unlink account [{resp.text}] - [{resp.status_code}]')

    def accounts_stats(self) -> ArkPCloudAccountsStats:
        """
        Calculates accounts stats for all visible accounts

        Returns:
            ArkPCloudAccountsStats: _description_
        """
        self._logger.info('Calculating accounts statistics')
        accounts = list(itertools.chain.from_iterable([p.items for p in list(self.list_accounts())]))
        accounts_stats = ArkPCloudAccountsStats.model_construct()
        accounts_stats.accounts_count = len(accounts)

        # Get accounts per platform id
        platform_ids: Set[str] = {a.platform_id for a in accounts}
        accounts_stats.accounts_count_by_platform_id = {pi: len([a for a in accounts if a.platform_id == pi]) for pi in platform_ids}

        # Get accounts per safe name
        safe_names: Set[str] = {a.safe_name for a in accounts}
        accounts_stats.accounts_count_by_safe_name = {sn: len([a for a in accounts if a.safe_name == sn]) for sn in safe_names}

        return accounts_stats

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
