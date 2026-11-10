import itertools
import os
from http import HTTPStatus
from typing import Any, Dict, Final, Iterator, List, Set, Union

from overrides import overrides
from pydantic import ValidationError
from requests import Response
from requests.exceptions import JSONDecodeError

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common import ArkPage
from ark_sdk_python.common.env.ark_env_mapping import DEPLOY_ENV, AwsEnv
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.common import ArkAsyncRequestSettings, ArkStatus
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.ars.common import ArkARSFilter, ArkARSSortQuery
from ark_sdk_python.models.services.ars.requests import (
    ArkARSAccessRequest,
    ArkARSAccessRequestAsyncTask,
    ArkARSAccessRequestInfo,
    ArkARSAccessRequestResult,
    ArkARSAccessRequestsInfo,
    ArkARSAccessRequestsStats,
    ArkARSAccessRequestState,
    ArkARSCancelAccessRequest,
    ArkARSFinalizeAccessRequest,
    ArkARSGetAccessRequest,
    ArkARSSubmitAccessRequest,
)
from ark_sdk_python.models.services.ars.requests.ark_ars_access_request_survey import ArkARSAccessRequestSurvey
from ark_sdk_python.models.services.ars.requests.ark_ars_get_access_request_survey import ArkARSGetAccessRequestSurvey
from ark_sdk_python.models.services.ars.requests.ark_target_category import ArkTargetCategory
from ark_sdk_python.services.ark_service import ArkService
from ark_sdk_python.services.ars.requests.ark_ars_requests_async_request import ArkARSRequestsAsyncRequest

SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='ars-requests', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
ArkARSAccessRequestPage = ArkPage[Union[ArkARSAccessRequest, ArkARSAccessRequestInfo]]

ACCESS_REQUESTS_ROUTE: Final[str] = '/api/workflows/requests'
ACCESS_REQUEST_ROUTE: Final[str] = '/api/workflows/requests/{request_id}'
CANCEL_ACCESS_REQUEST_ROUTE: Final[str] = '/api/workflows/requests/{request_id}/cancel'
FINALIZE_ACCESS_REQUEST_ROUTE: Final[str] = '/api/workflows/requests/{request_id}/finalize'
SURVEY_ROUTE: Final[str] = '/api/workflows/request-forms/{categoryType}'

MAX_REQUESTS_LIST_ITERATIONS: Final[int] = 100


class ArkARSRequestsService(ArkService):
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        super().__init__(isp_auth)
        self.__isp_auth = isp_auth
        deploy_env = AwsEnv(os.getenv(DEPLOY_ENV, AwsEnv.PROD.value))
        self.__client: ArkISPServiceClient = ArkISPServiceClient.from_isp_auth(
            isp_auth=self.__isp_auth,
            service_name='uar' if deploy_env == AwsEnv.PROD else 'ars',
            refresh_connection_callback=self.__refresh_ars_auth,
        )

    def __refresh_ars_auth(self, client: ArkISPServiceClient) -> None:
        ArkISPServiceClient.refresh_client(client, self.__isp_auth)

    def __list_access_requests_with_filters(self, requests_filter: ArkARSFilter) -> Iterator[ArkARSAccessRequestPage]:
        read_count = 0
        iteration = 0
        params: Dict[str, Any] = {
            'extended': requests_filter.extended,
            'limit': requests_filter.pagination.limit,
        }
        if requests_filter.pagination.offset:
            params['offset'] = requests_filter.pagination.offset
        if requests_filter.pagination.sort:
            params['sort'] = self._parse_sort_parameter(requests_filter.pagination.sort)
        if requests_filter.filter:
            params['filter'] = requests_filter.filter
        while iteration < MAX_REQUESTS_LIST_ITERATIONS:
            iteration += 1
            resp: Response = self.__client.get(
                ACCESS_REQUESTS_ROUTE,
                params=params,
            )
            if resp.status_code != HTTPStatus.OK:
                raise ArkServiceException(f'Failed to list access requests [{resp.text}] - [{resp.status_code}]')
            try:
                requests = ArkARSAccessRequestsInfo.model_validate(resp.json())
                yield ArkARSAccessRequestPage(items=requests.items)
                read_count += requests.count
                if read_count >= requests.total_count or requests.count < requests_filter.pagination.limit:
                    break
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse list access requests response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse list access requests response [{str(ex)}]') from ex

    @staticmethod
    def _parse_sort_parameter(sort: Union[ArkARSSortQuery, List[ArkARSSortQuery]]) -> str:
        if isinstance(sort, ArkARSSortQuery):
            sort = [sort]

        sort_list = []
        for sort_item in sort:
            if sort_item.field:
                sort_list.append(f"{sort_item.field} {sort_item.direction}" if sort_item.direction else f"{sort_item.field}")
        return ','.join(sort_list)

    def submit_access_request(self, submit_request: ArkARSSubmitAccessRequest) -> ArkARSRequestsAsyncRequest:
        """
        Submits a new access request
        Will return an async request to be used for polling

        Args:
            submit_request (ArkARSSubmitAccessRequest): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkARSRequestsAsyncRequest: _description_
        """
        self._logger.info(f'Submitting a access request [{submit_request.target_category}]')
        if submit_request.association is not None and not submit_request.association.get('association_id'):
            submit_request.association = None
        resp: Response = self.__client.post(
            ACCESS_REQUESTS_ROUTE,
            json=submit_request.model_dump(
                exclude={
                    'poll',
                    'poll_timeout_seconds',
                    'poll_progress_callback',
                    'poll_allow_refreshable_connection',
                }
            ),
        )
        if resp.status_code == HTTPStatus.OK:
            try:
                request = ArkARSAccessRequest.model_validate(resp.json())
                req = ArkARSRequestsAsyncRequest(
                    client=self.__client,
                    async_task=ArkARSAccessRequestAsyncTask(
                        task_id=request.request_id,
                        request=request,
                        action='StartRequest',
                        target_statuses=[ArkStatus.Success] if submit_request.wait_until_finished else [ArkStatus.Pending],
                    ),
                    async_request_settings=ArkAsyncRequestSettings(
                        poll_allow_refreshable_connection=submit_request.poll_allow_refreshable_connection
                    ),
                )
                if submit_request.poll:
                    req.poll(submit_request.poll_timeout_seconds, submit_request.poll_progress_callback)
                return req
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse submit access request response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse submit access request response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to submit access request [{resp.text}] - [{resp.status_code}]')

    def cancel_access_request(self, cancel_request: ArkARSCancelAccessRequest) -> ArkARSRequestsAsyncRequest:
        """
        Cancels a access request
        Will return an async request to be used for polling

        Args:
            cancel_request (ArkARSCancelAccessRequest): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkARSRequestsAsyncRequest: _description_
        """
        self._logger.info(f'Canceling a access request [{cancel_request.request_id}]')
        resp: Response = self.__client.post(
            CANCEL_ACCESS_REQUEST_ROUTE.format(request_id=cancel_request.request_id),
            json=cancel_request.model_dump(
                exclude={
                    'request_id',
                    'poll',
                    'poll_timeout_seconds',
                    'poll_progress_callback',
                    'poll_allow_refreshable_connection',
                }
            ),
        )
        if resp.status_code == HTTPStatus.OK:
            try:
                request = ArkARSAccessRequest.model_validate(resp.json())
                req = ArkARSRequestsAsyncRequest(
                    client=self.__client,
                    async_task=ArkARSAccessRequestAsyncTask(
                        task_id=request.request_id,
                        request=request,
                        action='CancelRequest',
                        target_statuses=[ArkStatus.Success],
                    ),
                    async_request_settings=ArkAsyncRequestSettings(
                        poll_allow_refreshable_connection=cancel_request.poll_allow_refreshable_connection
                    ),
                )
                if cancel_request.poll:
                    req.poll(cancel_request.poll_timeout_seconds, cancel_request.poll_progress_callback)
                return req
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse cancel access request response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse cancel access request response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to cancel access request [{resp.text}] - [{resp.status_code}]')

    def finalize_access_request(self, finalize_request: ArkARSFinalizeAccessRequest) -> ArkARSRequestsAsyncRequest:
        """
        Finalizes a access request
        Will return an async request to be used for polling

        Args:
            finalize_request (ArkARSFinalizeAccessRequest): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkARSRequestsAsyncRequest: _description_
        """
        self._logger.info(f'Finalizing a access request [{finalize_request.request_id}]')
        resp: Response = self.__client.post(
            FINALIZE_ACCESS_REQUEST_ROUTE.format(request_id=finalize_request.request_id),
            json=finalize_request.model_dump(
                exclude={
                    'request_id',
                    'poll',
                    'poll_timeout_seconds',
                    'poll_progress_callback',
                    'poll_allow_refreshable_connection',
                }
            ),
        )
        if resp.status_code == HTTPStatus.OK:
            try:
                request = ArkARSAccessRequest.model_validate(resp.json())
                req = ArkARSRequestsAsyncRequest(
                    client=self.__client,
                    async_task=ArkARSAccessRequestAsyncTask(
                        task_id=request.request_id,
                        request=request,
                        action='FinalizeRequest',
                        target_statuses=(
                            [ArkStatus.Success] if finalize_request.wait_until_finished else [ArkStatus.Pending, ArkStatus.Success]
                        ),
                    ),
                    async_request_settings=ArkAsyncRequestSettings(
                        poll_allow_refreshable_connection=finalize_request.poll_allow_refreshable_connection
                    ),
                )
                if finalize_request.poll:
                    req.poll(finalize_request.poll_timeout_seconds, finalize_request.poll_progress_callback)
                return req
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse finalize access request response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse finalize access request response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to finalize access request [{resp.text}] - [{resp.status_code}]')

    def list_access_requests(self) -> Iterator[ArkARSAccessRequestPage]:
        """
        Lists all access requests

        Raises:
            ArkServiceException: _description_

        Yields:
            ArkARSAccessRequestPage: _description_
        """
        self._logger.info('Listing all access requests')
        yield from self.__list_access_requests_with_filters(ArkARSFilter())

    def list_access_requests_by(self, requests_filters: ArkARSFilter) -> Iterator[ArkARSAccessRequestPage]:
        """
        Lists access requests by filters

        Args:
            requests_filters (ArkARSFilter): _description_

        Raises:
            ArkServiceException: _description_

        Yields:
            ArkARSAccessRequestPage: _description_
        """
        self._logger.info(f'Listing access requests with filters [{requests_filters}]')
        yield from self.__list_access_requests_with_filters(requests_filters)

    def access_request(self, get_request: ArkARSGetAccessRequest) -> ArkARSAccessRequest:
        """
        Gets a access request

        Args:
            get_request (ArkARSGetAccessRequest): _description_

        Raises:
            ArkServiceException: _description_

        Returns:
            ArkARSAccessRequest: _description_
        """
        self._logger.info(f'Getting a access request [{get_request.request_id}]')
        resp: Response = self.__client.get(
            ACCESS_REQUEST_ROUTE.format(request_id=get_request.request_id),
        )
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkARSAccessRequest.model_validate(resp.json())
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse get access request response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse get access request response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to get access request [{resp.text}] - [{resp.status_code}]')

    def access_requests_stats(self) -> ArkARSAccessRequestsStats:
        """
        Calculates access requests statistics.

        Returns:
            ArkARSAccessRequestsStats: _description_
        """
        self._logger.info('Calculating access requests stats')
        access_requests = list(itertools.chain.from_iterable([p.items for p in list(self.list_access_requests())]))
        access_requests_stats = ArkARSAccessRequestsStats.model_construct()
        access_requests_stats.requests_count = len(access_requests)

        # Count requests per category
        category_types: Set[ArkTargetCategory] = {e.target_category for e in access_requests if e.target_category}
        access_requests_stats.requests_count_by_category = {
            ct: len([e for e in access_requests if e.target_category and e.target_category == ct]) for ct in category_types
        }

        # Count requests per state
        state_types: Set[ArkARSAccessRequestState] = {e.request_state for e in access_requests if e.request_state}
        access_requests_stats.requests_count_by_state = {
            st: len([e for e in access_requests if e.request_state and e.request_state == st]) for st in state_types
        }

        # Count requests per result
        result_types: Set[ArkARSAccessRequestResult] = {e.request_result for e in access_requests if e.request_result}
        access_requests_stats.requests_count_by_result = {
            rt: len([e for e in access_requests if e.request_result and e.request_result == rt]) for rt in result_types
        }

        return access_requests_stats

    def access_request_survey(self, get_survey_request: ArkARSGetAccessRequestSurvey) -> ArkARSAccessRequestSurvey:
        """
        Gets an access request survey for a given category type.

        Args:
            get_survey_request (ArkARSGetAccessRequestSurvey): The request model containing the category type and request type.

        Raises:
            ArkServiceException: If the request fails or the response cannot be parsed.

        Returns:
            ArkARSAccessRequestSurvey: The access request survey response.
        """
        dumped = get_survey_request.model_dump()
        target_category = dumped['target_category']
        request_type = dumped['request_type']
        self._logger.info(f'Getting access request survey for target category [{target_category}] and request type [{request_type}]')
        resp: Response = self.__client.get(
            SURVEY_ROUTE.format(categoryType=target_category),
            params={'requestType': request_type},
        )
        if resp.status_code == HTTPStatus.OK:
            try:
                return ArkARSAccessRequestSurvey.model_validate(resp.json())
            except (ValidationError, JSONDecodeError, KeyError) as ex:
                self._logger.exception(f'Failed to parse access request survey response [{str(ex)}] - [{resp.text}]')
                raise ArkServiceException(f'Failed to parse access request survey response [{str(ex)}]') from ex
        raise ArkServiceException(f'Failed to get access request survey [{resp.text}] - [{resp.status_code}]')

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
