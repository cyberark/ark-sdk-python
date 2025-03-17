import itertools
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Dict, Final, Iterator, Optional, Set

from dateutil.tz import tzutc
from overrides import overrides

from ark_sdk_python.auth.ark_isp_auth import ArkISPAuth
from ark_sdk_python.common import ArkPage
from ark_sdk_python.common.isp import ArkISPServiceClient
from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.common import ArkApplicationCode, ArkProtocolType, ArkWorkspaceType
from ark_sdk_python.models.services import ArkServiceConfig
from ark_sdk_python.models.services.sm import (
    ArkSMGetSession,
    ArkSMGetSessionActivities,
    ArkSMSession,
    ArkSMSessionActivities,
    ArkSMSessionActivitiesFilter,
    ArkSMSessionActivity,
    ArkSMSessions,
    ArkSMSessionsFilter,
    ArkSMSessionsStats,
    ArkSMSessionStatus,
)
from ark_sdk_python.services.ark_service import ArkService

UTC = tzutc()
SERVICE_CONFIG: Final[ArkServiceConfig] = ArkServiceConfig(
    service_name='sm', required_authenticator_names=['isp'], optional_authenticator_names=[]
)
DEFAULT_TIME_DELTA_DAYS: Final[int] = 30
SESSIONS_API_URL: Final[str] = 'api/sessions'
SESSION_API_URL: Final[str] = 'api/sessions/{session_id}'
SESSION_ACTIVITIES_API_URL: Final[str] = 'api/sessions/{session_id}/activities'

ArkSMPage = ArkPage[ArkSMSession]
ArkSMActivitiesPage = ArkPage[ArkSMSessionActivity]


class ArkSMService(ArkService):
    def __init__(self, isp_auth: ArkISPAuth) -> None:
        super().__init__(isp_auth)
        self.__isp_auth = isp_auth
        self.__client: ArkISPServiceClient = ArkISPServiceClient.from_isp_auth(
            isp_auth=self.__isp_auth,
            service_name='sessionmonitoring',
            refresh_connection_callback=self.__refresh_sm_auth,
        )

    def __refresh_sm_auth(self, client: ArkISPServiceClient) -> None:
        ArkISPServiceClient.refresh_client(client, self.__isp_auth)

    def __search_params_from_filter(self, sessions_filter: ArkSMSessionsFilter):
        return {'search': sessions_filter.search}

    def __call_sessions_api(self, params: Optional[dict] = None) -> ArkSMSessions:
        params_dict = {}
        if params:
            params_dict['params'] = params
        resp = self.__client.get(SESSIONS_API_URL, **params_dict)
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to list sessions [{resp.text}] {params=}')
        return ArkSMSessions.model_validate(resp.json())

    def __call_activities_api(self, session_id: str, params: Optional[dict] = None) -> ArkSMSessionActivities:
        endpoint = SESSION_ACTIVITIES_API_URL.format(session_id=session_id)
        resp = self.__client.get(endpoint, params=params)
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to list activities [{resp.text}]')
        return ArkSMSessionActivities.model_validate(resp.json())

    def __list_sessions(self, params: Optional[Dict] = None) -> Iterator[ArkSMPage]:
        params = params or {}
        sessions: ArkSMSessions = self.__call_sessions_api(params)
        offset = 0
        while sessions.returned_count > 0:
            yield ArkSMPage(items=sessions.sessions)
            offset += sessions.returned_count
            params['offset'] = offset
            sessions = self.__call_sessions_api(params)

    def __list_activities(self, session_id: str, params: Optional[Dict] = None) -> Iterator[ArkSMActivitiesPage]:
        params = params or {}
        activities: ArkSMSessionActivities = self.__call_activities_api(session_id=session_id, params=params)
        offset = 0
        while activities.returned_count > 0:
            yield ArkSMActivitiesPage(items=activities.activities)
            offset += activities.returned_count
            params['offset'] = offset
            activities = self.__call_activities_api(session_id=session_id, params=params)

    def list_sessions(self) -> Iterator[ArkSMPage]:
        """
        Lists all sessions done on the last 24 hours

        Raises:
            ArkServiceException: _description_

        Yields:
            Iterator[ArkSMPage]: _description_
        """
        self._logger.info('Listing all session')
        yield from self.__list_sessions()

    def count_sessions(self) -> int:
        """
        Counts all sessions done on the last 24 hours

        Returns:
            int: _description_
        """
        return self.__call_sessions_api().filtered_count

    def list_sessions_by(self, sessions_filter: ArkSMSessionsFilter) -> Iterator[ArkSMPage]:
        """
        Lists all sessions with given filter

        Args:
            sessions_filter (ArkSMSessionsFilter): _description_
        Examples:
            ArkSMSessionsFilter(search='startTime GE 2023-12-03T08:55:29Z AND sessionDuration GE 00:00:01')
            ArkSMSessionsFilter(search='sessionStatus IN Failed,Ended AND endReason STARTSWITH Err008')
            ArkSMSessionsFilter(search='command STARTSWITH ls')
            ArkSMSessionsFilter(search='protocol IN SSH,RDP,Database')

        Raises:
            ArkServiceException: _description_

        Yields:
            Iterator[ArkSMPage]: _description_
        """
        self._logger.info(f'Listing sessions by filter: {sessions_filter.search}')
        yield from self.__list_sessions(self.__search_params_from_filter(sessions_filter))

    def count_sessions_by(self, sessions_filter: ArkSMSessionsFilter) -> int:
        """
        Counts all sessions with given filter

        Args:
            sessions_filter (ArkSMSessionsFilter): _description_
        Examples:
            ArkSMSessionsFilter(search='startTime GE 2023-12-03T08:55:29Z AND sessionDuration GE 00:00:01')
            ArkSMSessionsFilter(search='sessionStatus IN Failed,Ended AND endReason STARTSWITH Err008')
            ArkSMSessionsFilter(search='command STARTSWITH ls')
            ArkSMSessionsFilter(search='protocol IN SSH,RDP,Database')

        Returns:
            int: _description_
        """
        return self.__call_sessions_api(self.__search_params_from_filter(sessions_filter)).filtered_count

    def session(self, get_session: ArkSMGetSession) -> ArkSMSession:
        """
        Retrieves a session by id

        Args:
            get_session (ArkSMGetSession): _description_

        Raises:
            ArkServiceException: _description_
            ArkServiceException: _description_

        Returns:
            ArkSMSession: _description_
        """
        self._logger.info(f'Retrieving session by id [{get_session.session_id}]')
        resp = self.__client.get(SESSION_API_URL.format(session_id=get_session.session_id))
        if resp.status_code != HTTPStatus.OK:
            raise ArkServiceException(f'Failed to list sessions [{resp.text}]')
        session = resp.json()
        if len(session) == 0:
            raise ArkServiceException(f'No session found for requested session id [{get_session.session_id}]')
        return ArkSMSession.model_validate(session)

    def list_session_activities(self, get_session_activities: ArkSMGetSessionActivities) -> Iterator[ArkSMActivitiesPage]:
        """
        Lists all session activities by session id

        Args:
            get_session_activities (ArkSMGetSessionActivities): _description_

        Yields:
            Iterator[ArkSMActivitiesPage]: _description_
        """
        self._logger.info(f'Retrieving session activities by id [{get_session_activities.session_id}]')
        yield from self.__list_activities(session_id=get_session_activities.session_id)

    def count_session_activities(self, get_session_activities: ArkSMGetSessionActivities) -> int:
        """
        Count all session activities by session id

        Args:
            get_session_activities (ArkSMGetSessionActivities): _description_

        Returns:
            int: _description_
        """
        self._logger.info(f'Counting session activities by id [{get_session_activities.session_id}]')
        return self.__call_activities_api(session_id=get_session_activities.session_id).filtered_count

    def list_session_activities_by(self, session_activities_filter: ArkSMSessionActivitiesFilter) -> Iterator[ArkSMActivitiesPage]:
        """
        Lists all session activities for session id by filter

        Args:
            session_activities_filter (ArkSMSessionActivitiesFilter): _description_

        Yields:
            Iterator[ArkSMActivitiesPage]: _description_
        """
        self._logger.info(f'Retrieving session activities by id [{session_activities_filter.session_id}]')
        for page in self.__list_activities(session_id=session_activities_filter.session_id):
            yield ArkSMActivitiesPage(
                items=[activity for activity in page.items if session_activities_filter.command_contains in activity.command]
            )

    def count_session_activities_by(self, session_activities_filter: ArkSMSessionActivitiesFilter) -> int:
        """
        Count all session activities for session id by filter

        Args:
            session_activities_filter (ArkSMSessionActivitiesFilter): _description_

        Returns:
            int: _description_
        """
        count = 0
        self._logger.info(f'Counting session activities by id [{session_activities_filter.session_id}] and filter')
        for page in self.list_session_activities_by(session_activities_filter):
            count += len(page.items)
        return count

    def sessions_stats(self) -> ArkSMSessionsStats:
        """
        Returns statistics about the sessions in the last 30 days

        Returns:
            ArkSMSessionsStats: _description_
        """
        self._logger.info('Calculating sessions stats for the last 30 days')
        start_time_from = (datetime.now() - timedelta(days=30)).isoformat(timespec='seconds') + 'Z'
        sessions = list(
            itertools.chain.from_iterable(
                [p.items for p in self.list_sessions_by(ArkSMSessionsFilter(search=f'startTime ge {start_time_from}'))]
            )
        )
        sessions_stats = ArkSMSessionsStats.model_construct()
        sessions_stats.sessions_count = len(sessions)
        sessions_stats.sessions_failure_count = len([s for s in sessions if s.session_status == ArkSMSessionStatus.FAILED])

        # Get sessions per application code
        app_codes: Set[ArkApplicationCode] = {s.application_code for s in sessions}
        sessions_stats.sessions_count_per_application_code = {
            ac: len([s for s in sessions if s.application_code == ac]) for ac in app_codes
        }

        # Get sessions per platform
        platforms: Set[ArkWorkspaceType] = {s.platform for s in sessions}
        sessions_stats.sessions_count_per_platform = {p: len([s for s in sessions if s.platform == p]) for p in platforms}

        # Get sessions per protocol
        protocols: Set[ArkProtocolType] = {s.protocol for s in sessions}
        sessions_stats.sessions_count_per_protocol = {p: len([s for s in sessions if s.protocol == p]) for p in protocols}

        # Get sessions per status
        statuses: Set[ArkSMSessionStatus] = {s.session_status for s in sessions}
        sessions_stats.sessions_count_per_status = {st: len([s for s in sessions if s.session_status == st]) for st in statuses}

        return sessions_stats

    @staticmethod
    @overrides
    def service_config() -> ArkServiceConfig:
        return SERVICE_CONFIG
