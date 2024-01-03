from datetime import datetime, timedelta

from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.models.ark_profile import ArkProfileLoader
from ark_sdk_python.models.common import ArkProtocolType
from ark_sdk_python.models.services.sm import ArkSMGetSession, ArkSMGetSessionActivities, ArkSMSessionsFilter
from ark_sdk_python.services.sm import ArkSMService

if __name__ == "__main__":
    isp_auth = ArkISPAuth()
    isp_auth.authenticate(profile=ArkProfileLoader().load_default_profile())
    sm: ArkSMService = ArkSMService(isp_auth)
    search_by = 'startTime ge {start_time_from} AND sessionDuration GE {min_duration} AND protocol IN {protocols}'
    search_by = search_by.format(
        start_time_from=(datetime.utcnow() - timedelta(days=30)).isoformat(timespec='seconds'),
        min_duration='00:00:01',
        protocols=','.join([ArkProtocolType.DB[0], ArkProtocolType.SSH[0], ArkProtocolType.RDP[0]]),
    )
    sessions_filter = ArkSMSessionsFilter(
        search=search_by,
    )
    print(f'session_count = {sm.count_sessions_by(sessions_filter)}')
    for s_page in sm.list_sessions_by(sessions_filter):
        for session in s_page.items:
            session = sm.session(ArkSMGetSession(session_id=session.session_id))
            get_session_activities = ArkSMGetSessionActivities(session_id=session.session_id)
            print(f'session = {session}, activities_count = {sm.count_session_activities(get_session_activities)}')
            session_activities = [activity for page in sm.list_session_activities(get_session_activities) for activity in page.items]
            print(session_activities)
