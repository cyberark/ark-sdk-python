"""
One-time license consumption analytics (SCA / SIA ZSP / Privilege Cloud) for a single tenant.

Flow:
    1. Collect every user in the Identity directory (suspended users included) - users that are not there are dropped
    2. PrivCloud usage - members (recursively through nested roles) of the PrivCloud *human* roles, or with --pcloud-by-user-roles
       the other way around: the roles of every Identity user (UserMgmt/GetUsersRolesAndAdministrativeRights), which also covers
       users that are only in those roles through a group that can't be expanded from the role
    3. SIA ZSP / SCA usage - sessions from session monitoring in the given timeframe
    4. Split the users into exactly one of 7 groups according to what they used
       (--active-only first leaves out users whose account is Locked / Disabled / Expired, listing them separately)

Output: stdout + JSON + Excel (Excel requires `pip install openpyxl`).

Usage:
    python license_consumption_analytics.py --username user@cyberark.cloud.1234 --secret ... [--service-user] --output-dir ./out
    (the secret can also come from the ARK_SECRET env variable)
    (only counts are reported, add --include-usernames to also save and print the usernames)
    (timeframe defaults to the last 365 days up to now, override with --start / --end, UTC ISO)
"""

import argparse
import json
import logging
import os
import queue
import random
import re
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable, Dict, Final, Iterable, List, Optional, Set, TypeVar

import requests
from requests.adapters import HTTPAdapter

from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.common.ark_logger import get_logger
from ark_sdk_python.models.ark_exceptions import ArkServiceException
from ark_sdk_python.models.auth import (
    ArkAuthMethod,
    ArkAuthProfile,
    ArkSecret,
    IdentityArkAuthMethodSettings,
    IdentityServiceUserArkAuthMethodSettings,
)
from ark_sdk_python.models.common import ArkAccessMethod, ArkApplicationCode
from ark_sdk_python.models.common.identity import DirectoryService
from ark_sdk_python.models.services.identity.directories import (
    ArkIdentityEntityType,
    ArkIdentityListDirectories,
    ArkIdentityListDirectoriesEntities,
)
from ark_sdk_python.models.services.identity.roles import ArkIdentityListRoleMembers, ArkIdentityRoleIdByName
from ark_sdk_python.models.services.identity.users import ArkIdentityGetUserState, ArkIdentityListUserRoles
from ark_sdk_python.models.services.pcloud.usermgmt import ArkPCloudVaultUsersFilter
from ark_sdk_python.models.services.sm import ArkSMSessionsFilter, ArkSMSessionStatus
from ark_sdk_python.services.identity.directories import ArkIdentityDirectoriesService
from ark_sdk_python.services.identity.federations import ArkIdentityFederationsService
from ark_sdk_python.services.identity.roles import ArkIdentityRolesService
from ark_sdk_python.services.identity.users import ArkIdentityUsersService
from ark_sdk_python.services.pcloud.usermgmt import ArkPCloudUserMgmtService
from ark_sdk_python.services.sm import ArkSMService

LOGGER_NAME: Final[str] = 'license-consumption'
logger = logging.getLogger(LOGGER_NAME)  # configured in main through get_logger, which returns this same logger

# Human roles only. Service user type / system permission roles and group roles are intentionally not counted.
PCLOUD_HUMAN_ROLES: Final[List[str]] = [
    f'Privilege Cloud {kind}{suffix}'
    for suffix in ('', ' Lite', ' Basic')
    for kind in ('Administrators', 'Auditors', 'Safe Managers', 'Users')
] + ['Privilege Cloud External Vendors']

# Session monitoring classification
SCA_APPLICATION_CODES: Final[Set[ArkApplicationCode]] = {ArkApplicationCode.SCA}
SIA_APPLICATION_CODES: Final[Set[ArkApplicationCode]] = {ArkApplicationCode.SIA, ArkApplicationCode.DPA}
ZSP_ACCESS_METHODS: Final[Set[ArkAccessMethod]] = {ArkAccessMethod.JIT}  # any other access method is not ZSP

DEFAULT_LOOKBACK_DAYS: Final[int] = 365
ENTITIES_LIMIT: Final[int] = 1_000_000
DEFAULT_MAX_WORKERS: Final[int] = 128
DEFAULT_SESSIONS_WORKERS: Final[int] = 8
DEFAULT_SESSIONS_PAGE_SIZE: Final[int] = 1000
DEFAULT_VAULT_PAGE_SIZE: Final[int] = 200
GROUP_SEARCH_LIMIT: Final[int] = 1000
UNKNOWN_DIRECTORY: Final[str] = 'Unknown'

SCA, ZSP, PCLOUD = 'SCA', 'SIA ZSP', 'PrivCloud'
GROUPS: Final[Dict[str, frozenset]] = {
    'SCA + SIA ZSP + PrivCloud': frozenset({SCA, ZSP, PCLOUD}),
    'SCA + SIA ZSP': frozenset({SCA, ZSP}),
    'SIA ZSP + PrivCloud': frozenset({ZSP, PCLOUD}),
    'SCA + PrivCloud': frozenset({SCA, PCLOUD}),
    'PrivCloud only': frozenset({PCLOUD}),
    'SIA ZSP only': frozenset({ZSP}),
    'SCA only': frozenset({SCA}),
}


@dataclass
class Usage:
    sca: Set[str] = field(default_factory=set)
    zsp: Set[str] = field(default_factory=set)
    pcloud: Set[str] = field(default_factory=set)
    pcloud_groups: List[Dict[str, str]] = field(default_factory=list)  # groups found as members of the PrivCloud roles
    excluded_inactive: Dict[str, List[Dict[str, str]]] = field(
        default_factory=dict
    )  # product -> inactive users left out with --active-only
    not_in_vault: List[str] = field(default_factory=list)  # PrivCloud role holders that were never provisioned to the vault
    role_lookup_failed: List[str] = field(default_factory=list)  # users whose roles couldn't be read
    state_lookup_failed: List[str] = field(default_factory=list)  # users whose account state couldn't be read
    notes: List[str] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)


def _norm(name: Optional[str]) -> Optional[str]:
    return name.strip().lower() if name and name.strip() else None


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)


def _fmt_time(value: datetime) -> str:
    return value.strftime('%Y-%m-%dT%H:%M:%SZ')


def _day_windows(start: datetime, end: datetime) -> Iterable[tuple]:
    """
    Splits the timeframe to UTC day windows. The sessions API pages by offset, which gets slower the deeper it goes, so many small
    windows are faster than a few big ones, and they can be fetched in parallel.
    """
    cursor = start
    while cursor < end:
        nxt = datetime(cursor.year, cursor.month, cursor.day, tzinfo=timezone.utc) + timedelta(days=1)
        yield cursor, min(nxt, end)
        cursor = nxt


def collect_identity_users(isp_auth: ArkISPAuth, user_ids: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Returns {normalized username: display username} of every user in the Identity directory (suspended included).
    When `user_ids` is given, it is filled with {normalized username: user id}
    """
    service = ArkIdentityDirectoriesService(isp_auth)
    users: Dict[str, str] = {}
    logger.info('Listing identity directory users')
    for page in service.list_directories_entities(
        ArkIdentityListDirectoriesEntities(
            directories=[DirectoryService.Identity],
            entity_types=[ArkIdentityEntityType.User],
            page_size=ENTITIES_LIMIT,
            limit=ENTITIES_LIMIT,
        )
    ):
        for entity in page.items:
            if key := _norm(entity.name):
                users[key] = entity.name
                if user_ids is not None:
                    user_ids[key] = entity.id
    logger.info(f'Found [{len(users)}] identity users')
    if len(users) >= ENTITIES_LIMIT:
        logger.warning(f'Identity users reached the query limit [{ENTITIES_LIMIT}], the list may be truncated')
    return users


def collect_directories(isp_auth: ArkISPAuth) -> List[Dict[str, str]]:
    """Lists the directories of the tenant (Cloud Directory, Active Directory, federated), with their type, name and id"""
    logger.info('Listing the identity directories')
    try:
        directories = ArkIdentityDirectoriesService(isp_auth).list_directories(ArkIdentityListDirectories())
    except Exception as ex:  # pylint: disable=broad-except
        logger.warning(f'Failed listing the directories: {ex}')
        return []
    result = [
        {
            'type': directory.directory.value,
            'name': directory.display_name or '',
            'config': directory.config or '',
            'directory_service_uuid': directory.directory_service_uuid,
        }
        for directory in directories
    ]
    logger.info(f'Found [{len(result)}] directories: {[(d["type"], d["name"] or d["config"]) for d in result]}')
    return result


def collect_federations(isp_auth: ArkISPAuth) -> List[Dict[str, str]]:
    """Lists the external identity providers (SAML 2.0 / OIDC federations) of the tenant"""
    logger.info('Listing the identity federations')
    try:
        federations = ArkIdentityFederationsService(isp_auth).list_federations()
    except Exception as ex:  # pylint: disable=broad-except
        logger.warning(f'Failed listing the federations: {ex}')
        return []
    result = [
        {
            'federation_id': f.federation_id,
            'name': f.federation_name,
            'type': f.federation_type,
            'active': 'yes' if f.active else 'no',
            'domains': ', '.join(f.domains),
        }
        for f in federations
    ]
    logger.info(f'Found [{len(result)}] federations: {[(f["name"], f["type"], f["active"]) for f in result]}')
    return result


def _resolve_group_directory(
    directories_service: ArkIdentityDirectoriesService, group_id: str, group_name: str, cache: Dict[str, Dict[str, str]]
) -> Dict[str, str]:
    """Directory type (CDS / AdProxy / FDS) and directory name of a group member, by searching the directories for the group"""
    if group_id in cache:
        return cache[group_id]
    found = {'directory_type': UNKNOWN_DIRECTORY, 'directory_name': UNKNOWN_DIRECTORY}
    try:
        candidates = [
            entity
            for page in directories_service.list_directories_entities(
                ArkIdentityListDirectoriesEntities(
                    entity_types=[ArkIdentityEntityType.Group], search=group_name, page_size=GROUP_SEARCH_LIMIT, limit=GROUP_SEARCH_LIMIT
                )
            )
            for entity in page.items
        ]
        # An id match is exact, a name match is the fallback when the role member guid differs from the directory entity id
        match = next((e for e in candidates if e.id == group_id), None) or next(
            (e for e in candidates if _norm(e.name) == _norm(group_name) or _norm(e.display_name) == _norm(group_name)), None
        )
        if match:
            found = {'directory_type': match.directory_service_type.value, 'directory_name': match.service_instance_localized}
        else:
            logger.warning(f'Group [{group_name}] [{group_id}] was not found in any directory, its directory type is unknown')
    except Exception as ex:  # the directory is informative only, it must not stop the run
        logger.warning(f'Failed resolving the directory of group [{group_name}] [{group_id}]: {ex}')
    cache[group_id] = found
    return found


def collect_pcloud_users(isp_auth: ArkISPAuth, usage: Usage) -> None:
    """
    Members of the PrivCloud human roles, expanding nested roles.
    Group members can't be expanded with the current SDK, they are recorded in `usage.pcloud_groups` with their directory type
    """
    roles_service = ArkIdentityRolesService(isp_auth)
    directories_service = ArkIdentityDirectoriesService(isp_auth)
    visited: Set[str] = set()
    seen_groups: Set[tuple] = set()
    directory_cache: Dict[str, Dict[str, str]] = {}

    def _walk(human_role: str, role_name: Optional[str] = None, role_id: Optional[str] = None, nested_in: str = '') -> None:
        members = roles_service.list_role_members(ArkIdentityListRoleMembers(role_name=role_name, role_id=role_id))
        logger.debug(f'Role [{role_name or role_id}] has [{len(members)}] direct members')
        for member in members:
            if member.member_type == ArkIdentityEntityType.User:
                if key := _norm(member.member_name):
                    usage.pcloud.add(key)
            elif member.member_type == ArkIdentityEntityType.Role:
                if member.member_id not in visited:
                    visited.add(member.member_id)
                    logger.debug(f'Expanding nested role [{member.member_name}]')
                    _walk(human_role, role_id=member.member_id, nested_in=member.member_name)
            elif (human_role, member.member_id) not in seen_groups:
                seen_groups.add((human_role, member.member_id))
                directory = _resolve_group_directory(directories_service, member.member_id, member.member_name, directory_cache)
                logger.info(
                    f'Role [{human_role}] has group member [{member.member_name}] of directory type [{directory["directory_type"]}] '
                    f'([{directory["directory_name"]}]), not expanded'
                )
                usage.pcloud_groups.append(
                    {
                        'role': human_role,
                        'nested_role': nested_in,
                        'group_name': member.member_name,
                        'group_id': member.member_id,
                        **directory,
                    }
                )

    for role_name in PCLOUD_HUMAN_ROLES:
        before = len(usage.pcloud)
        try:
            _walk(role_name, role_name=role_name)
            logger.info(f'Role [{role_name}] done, [{len(usage.pcloud) - before}] new unique users (total [{len(usage.pcloud)}])')
        except Exception as ex:  # a role that doesn't exist on the tenant must not stop the run
            logger.warning(f'Role [{role_name}] skipped: {ex}')
            usage.notes.append(f'Role [{role_name}] skipped: {ex}')
    if usage.pcloud_groups:
        by_directory: Dict[str, int] = {}
        for entry in usage.pcloud_groups:
            by_directory[entry['directory_type']] = by_directory.get(entry['directory_type'], 0) + 1
        logger.warning(
            f'[{len(usage.pcloud_groups)}] group member(s) in PrivCloud roles were not expanded, by directory type: {by_directory}'
        )
        usage.notes.append(
            f'{len(usage.pcloud_groups)} group member(s) in PrivCloud roles were NOT expanded (no SDK API) - PrivCloud may be '
            f'under-counted, by directory type: {by_directory} (see pcloud_role_groups)'
        )


T = TypeVar('T')
LOOKUP_MAX_ATTEMPTS: Final[int] = 4
LOOKUP_MAX_DELAY_SECONDS: Final[int] = 16
RETRYABLE_STATUS_CODES: Final[Set[int]] = {429, 500, 502, 503, 504}
STATUS_IN_ERROR: Final[re.Pattern] = re.compile(r'\[(\d{3})\]\s*$')


def _is_transient(ex: Exception) -> bool:
    """Rate limiting (429), server errors (5xx), timeouts and connection errors are worth another attempt, anything else is final"""
    if isinstance(ex, (requests.ConnectionError, requests.Timeout)):
        return True
    if isinstance(ex, ArkServiceException):
        match = STATUS_IN_ERROR.search(str(ex.error))  # the service errors end with the http status, e.g. "... [body] - [429]"
        return bool(match) and int(match.group(1)) in RETRYABLE_STATUS_CODES
    return False


def call_with_retries(func: Callable[[], T], what: str) -> T:
    """Runs the per user call, retrying transient failures with an exponential backoff and jitter"""
    for attempt in range(1, LOOKUP_MAX_ATTEMPTS + 1):
        try:
            return func()
        except Exception as ex:  # pylint: disable=broad-except
            if attempt == LOOKUP_MAX_ATTEMPTS or not _is_transient(ex):
                raise
            delay = min(LOOKUP_MAX_DELAY_SECONDS, 2**attempt) * random.uniform(0.5, 1.0)
            logger.warning(
                f'{what} failed with a transient error, retrying in [{delay:.1f}] seconds (attempt [{attempt}/{LOOKUP_MAX_ATTEMPTS}]): {ex}'
            )
            time.sleep(delay)
    raise AssertionError('unreachable')  # pragma: no cover


def widen_connection_pool(service: ArkIdentityUsersService, size: int) -> None:
    """
    The SDK client keeps the default pool of 10 connections per host, so with more parallel workers the extra connections are
    discarded after each request ("Connection pool is full") and every call pays a new TLS handshake. Sizes the pool to the workers.
    """
    adapter = HTTPAdapter(pool_connections=size, pool_maxsize=size)
    service._client.session.mount('https://', adapter)  # pylint: disable=protected-access


def collect_pcloud_users_by_user_roles(isp_auth: ArkISPAuth, usage: Usage, user_ids: Dict[str, str], max_workers: int) -> None:
    """
    PrivCloud users resolved from the users side: the roles of each Identity user, taken from
    UserMgmt/GetUsersRolesAndAdministrativeRights, are checked against the PrivCloud human roles.
    Unlike the role members, this also catches users that hold a role only through a group.
    """
    roles_service = ArkIdentityRolesService(isp_auth)
    users_service = ArkIdentityUsersService(isp_auth)
    widen_connection_pool(users_service, max_workers)
    pcloud_roles: Set[str] = {_norm(name) for name in PCLOUD_HUMAN_ROLES}
    for name in PCLOUD_HUMAN_ROLES:
        try:  # a role missing on the tenant is fine, matching by name still works
            pcloud_roles.add(_norm(roles_service.role_id_by_name(ArkIdentityRoleIdByName(role_name=name))))
        except Exception as ex:  # pylint: disable=broad-except
            logger.debug(f'Role [{name}] has no id on the tenant: {ex}')

    def _is_pcloud_user(item: tuple) -> tuple:
        username, user_id = item
        roles = call_with_retries(
            lambda: users_service.list_user_roles(ArkIdentityListUserRoles(user_id=user_id)), f'Reading the roles of user id [{user_id}]'
        )
        return username, any(_norm(value) in pcloud_roles for role in roles for value in (role.role_id, role.name, role.role_name))

    logger.info(f'Resolving the roles of [{len(user_ids)}] identity users with [{max_workers}] workers')
    failed: List[str] = []
    done = 0
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_is_pcloud_user, item): item[0] for item in user_ids.items()}
        for future, username in futures.items():
            try:
                _, is_pcloud = future.result()
                if is_pcloud:
                    usage.pcloud.add(username)
            except Exception as ex:  # pylint: disable=broad-except
                failed.append(username)
                logger.warning(f'Failed resolving the roles of user id [{user_ids[username]}]: {ex}')
            done += 1
            if done % 500 == 0:
                logger.info(f'Resolved the roles of [{done}/{len(futures)}] users, [{len(usage.pcloud)}] PrivCloud users so far')
    usage.stats['pcloud_role_lookup_failed_users'] = len(failed)
    if failed:
        logger.warning(f'The roles of [{len(failed)}] users could not be resolved, PrivCloud may be under-counted')
        usage.role_lookup_failed = [identity_name for identity_name in sorted(failed)]


def list_vault_usernames(service: ArkPCloudUserMgmtService, page_size: int) -> Set[str]:
    """
    The normalized usernames of all the vault users, read in small pages (Get Users pageOffset / pageSize), without the extended
    details, since one big call can time out. A page that fails with a transient error is read again from the same offset.
    """
    names: Set[str] = set()
    offset = 0
    failures = 0
    while True:
        try:
            for page in service.list_vault_users_pages(
                ArkPCloudVaultUsersFilter(page_size=page_size, page_offset=offset, extended_details=False)
            ):
                names.update(_norm(user.username) for user in page.items)
                offset += len(page.items)
                failures = 0
                logger.info(f'Read [{offset}] vault users so far')
            names.discard(None)
            return names
        except Exception as ex:  # pylint: disable=broad-except
            failures += 1
            if failures >= LOOKUP_MAX_ATTEMPTS or not _is_transient(ex):
                raise
            delay = min(LOOKUP_MAX_DELAY_SECONDS, 2**failures) * random.uniform(0.5, 1.0)
            logger.warning(
                f'Listing the vault users from [{offset}] failed with a transient error, retrying in [{delay:.1f}] seconds: {ex}'
            )
            time.sleep(delay)


def validate_pcloud_in_vault(
    isp_auth: ArkISPAuth, usage: Usage, identity_users: Dict[str, str], page_size: int = DEFAULT_VAULT_PAGE_SIZE
) -> None:
    """
    Keeps among the PrivCloud users only those that exist in the vault. A user is provisioned to the vault automatically the first
    time it actually goes to PrivCloud, so a user that holds a PrivCloud role but never did is not a consumer. The vault users are
    listed once in pages (PCloud Get Users), not one call per user.
    """
    vault_names = list_vault_usernames(ArkPCloudUserMgmtService(isp_auth), page_size)
    if not vault_names:
        # a failed read must not look like "nobody was ever provisioned", which would empty the PrivCloud count
        raise RuntimeError('The vault returned no users, check that the user is allowed to list the vault users (Audit / Add-Update users)')
    missing = sorted((usage.pcloud & identity_users.keys()) - vault_names)  # the users not in Identity are dropped on their own
    usage.pcloud.difference_update(missing)
    usage.not_in_vault = missing
    usage.stats['vault_users_listed'] = len(vault_names)
    logger.info(f'The vault holds [{len(vault_names)}] users, [{len(missing)}] PrivCloud role holders are not in it and were excluded')


def exclude_inactive_users(
    isp_auth: ArkISPAuth, usage: Usage, identity_users: Dict[str, str], user_ids: Dict[str, str], max_workers: int
) -> None:
    """
    Removes from the usage the users whose account is not active, i.e. Locked / Disabled / Expired (UserMgmt/GetUserAttributes).
    Only the users that used something are checked. A user whose state can't be read is kept, and noted.
    """
    candidates = sorted((usage.sca | usage.zsp | usage.pcloud) & identity_users.keys())
    users_service = ArkIdentityUsersService(isp_auth)
    widen_connection_pool(users_service, max_workers)
    logger.info(f'Checking the account state of [{len(candidates)}] users that used a product with [{max_workers}] workers')
    inactive: Dict[str, str] = {}
    unknown: List[str] = []

    def _state(username: str) -> tuple:
        user_id = user_ids[username]
        return username, call_with_retries(
            lambda: users_service.user_state(ArkIdentityGetUserState(user_id=user_id)), f'Reading the state of user id [{user_id}]'
        )

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_state, username): username for username in candidates}
        for future, username in futures.items():
            try:
                _, user_state = future.result()
                if not user_state.is_active:
                    inactive[username] = user_state.state
            except Exception as ex:  # pylint: disable=broad-except
                unknown.append(username)
                logger.warning(f'Failed reading the state of user id [{user_ids[username]}], keeping it: {ex}')
    for product, users in ((SCA, usage.sca), (ZSP, usage.zsp), (PCLOUD, usage.pcloud)):
        usage.excluded_inactive[product] = [{'username': identity_users[u], 'state': inactive[u]} for u in sorted(users & inactive.keys())]
        users.difference_update(inactive)  # in place, `-=` with dict keys would only rebind the local
    logger.info(f'Excluded [{len(inactive)}] inactive users: {dict(Counter(inactive.values()))}')
    usage.stats['inactive_users_excluded'] = len(inactive)
    if unknown:
        usage.stats['user_state_lookup_failed_users'] = len(unknown)
        usage.state_lookup_failed = sorted(unknown)


def _fetch_window_sessions(sm: ArkSMService, win_start: datetime, win_end: datetime, page_size: Optional[int]) -> tuple:
    """
    All the sessions that started in the window, as ([(session id, application code, access method, user, failed)], largest page
    that the service returned)
    """
    search = f'startTime ge {_fmt_time(win_start)} AND startTime le {_fmt_time(win_end)}'
    rows: List[tuple] = []
    largest_page = 0
    for page in sm.list_sessions_by(ArkSMSessionsFilter(search=search, limit=page_size)):
        largest_page = max(largest_page, len(page.items))
        rows.extend(
            (s.session_id, s.application_code, s.access_method, _norm(s.user), s.session_status == ArkSMSessionStatus.FAILED)
            for s in page.items
        )
    return rows, largest_page


def _usable_page_size(sm: ArkSMService, end: datetime, page_size: Optional[int]) -> Optional[int]:
    """The requested page size when the sessions API accepts it (tried once on the last day), else None for the service default"""
    if not page_size:
        return None
    window_start = end - timedelta(days=1)
    search = f'startTime ge {_fmt_time(window_start)} AND startTime le {_fmt_time(end)}'
    try:
        next(iter(sm.list_sessions_by(ArkSMSessionsFilter(search=search, limit=page_size))), None)
        return page_size
    except Exception as ex:  # pylint: disable=broad-except
        logger.warning(f'The sessions API did not accept the page size [{page_size}], using its default page size: {ex}')
        return None


def collect_session_users(
    isp_auth: ArkISPAuth,
    start: datetime,
    end: datetime,
    usage: Usage,
    workers: int = DEFAULT_SESSIONS_WORKERS,
    page_size: Optional[int] = DEFAULT_SESSIONS_PAGE_SIZE,
) -> None:
    """
    Users with at least one non-failed SCA / SIA ZSP session in the timeframe, by session monitoring.
    The timeframe is split to day windows that are fetched in parallel, each worker with its own client. A window that fails with
    a transient error is fetched again from its start (the sessions are deduplicated by id, so that is safe).
    """
    windows = list(_day_windows(start, end))
    workers = max(1, min(workers, len(windows)))
    services: 'queue.Queue[ArkSMService]' = queue.Queue()
    for _ in range(workers):
        services.put(ArkSMService(isp_auth))
    page_size = _usable_page_size(services.queue[0], end, page_size)

    def _fetch(window: tuple) -> tuple:
        sm = services.get()
        try:
            return call_with_retries(
                lambda: _fetch_window_sessions(sm, *window, page_size), f'Fetching the sessions of [{_fmt_time(window[0])}]'
            )
        finally:
            services.put(sm)

    seen: Set[str] = set()
    breakdown: Dict[str, int] = {}
    largest_page = 0
    logger.info(
        f'Fetching the sessions of [{len(windows)}] day windows with [{workers}] workers, requested page size [{page_size or "default"}]'
    )
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_fetch, window): window for window in windows}
        for done, future in enumerate(as_completed(futures), start=1):
            rows, window_largest_page = future.result()
            largest_page = max(largest_page, window_largest_page)
            for session_id, application_code, access_method, user, failed in rows:
                if session_id in seen:
                    continue
                seen.add(session_id)
                is_sca = application_code in SCA_APPLICATION_CODES
                is_zsp = application_code in SIA_APPLICATION_CODES and access_method in ZSP_ACCESS_METHODS
                if is_sca or is_zsp:  # other sessions (SIA vaulted / unknown) are not counted and are not shown
                    label = f'{application_code}/{access_method if access_method else None}'
                    breakdown[label] = breakdown.get(label, 0) + 1
                if not user or failed:
                    continue
                if is_sca:
                    usage.sca.add(user)
                elif is_zsp:
                    usage.zsp.add(user)
            if done % 10 == 0 or done == len(windows):
                logger.info(
                    f'Fetched [{done}/{len(windows)}] day windows, totals so far: sessions [{len(seen)}], SCA users [{len(usage.sca)}], '
                    f'SIA ZSP users [{len(usage.zsp)}]'
                )
    usage.stats['sessions_total'] = len(seen)
    logger.info(f'The largest sessions page returned by the service held [{largest_page}] sessions')
    logger.info(f'Sessions by applicationCode/accessMethod: {json.dumps(breakdown, sort_keys=True)}')
    usage.notes.append(f'Sessions by applicationCode/accessMethod: {json.dumps(breakdown, sort_keys=True)}')


def compute_groups(usage: Usage, identity_users: Dict[str, str]) -> Dict[str, List[str]]:
    """Every identity user who used at least one product lands in exactly one group. Users missing from Identity are dropped"""
    members: Dict[str, Set[str]] = {}
    for product, users in ((SCA, usage.sca), (ZSP, usage.zsp), (PCLOUD, usage.pcloud)):
        for user in users & identity_users.keys():
            members.setdefault(user, set()).add(product)
    result: Dict[str, List[str]] = {name: [] for name in GROUPS}
    for user, products in members.items():
        for name, expected in GROUPS.items():
            if frozenset(products) == expected:
                result[name].append(identity_users[user])
    for product, users in ((SCA, usage.sca), (ZSP, usage.zsp), (PCLOUD, usage.pcloud)):
        if dropped := len(users - identity_users.keys()):
            logger.info(f'[{dropped}] {product} users are not in Identity anymore and were dropped')
    for name, users in result.items():
        logger.info(f'Group [{name}]: [{len(users)}] users')
    return {name: sorted(users, key=str.lower) for name, users in result.items()}


STAT_EXPLANATIONS: Final[Dict[str, str]] = {
    'sessions_total': 'Distinct sessions that session monitoring returned for the timeframe, before filtering failed ones and by product.',
    'vault_users_listed': 'Users that the vault returned (PCloud Get Users), the base of the PrivCloud vault validation.',
    'inactive_users_excluded': 'Distinct users that used a product but were left out because the account is Locked, Disabled or Expired.',
    'user_state_lookup_failed_users': 'Users whose account state could not be read, they were kept as active.',
    'pcloud_role_lookup_failed_users': 'Users whose roles could not be read, so PrivCloud may be under-counted.',
}
PRODUCT_SOURCES: Final[Dict[str, str]] = {SCA: 'Session monitoring', ZSP: 'Session monitoring', PCLOUD: 'Role membership'}
VAULT_VALIDATED_SOURCE: Final[str] = 'Role membership + vault validation'


def _product_descriptions(pcloud_by_user_roles: bool, validate_pcloud_vault: bool = False) -> Dict[str, str]:
    pcloud_source = (
        'the roles of every Identity user (UserMgmt/GetUsersRolesAndAdministrativeRights), which also covers roles held through groups'
        if pcloud_by_user_roles
        else 'the members of the roles, expanding nested roles. Groups inside a role are not expanded, so users that hold a role only '
        'through a group are missed (use --pcloud-by-user-roles to count them)'
    )
    return {
        SCA: 'Secure Cloud Access. A user is counted when it has at least one non-failed SCA session in the timeframe.',
        ZSP: 'SIA Zero Standing Privileges. A user is counted when it has at least one non-failed SIA / DPA session in the timeframe that '
        'used just-in-time (JIT) access.',
        PCLOUD: 'Privilege Cloud. A user is counted when it holds one of the PrivCloud human roles (Administrators, Auditors, Safe Managers, '
        f'Users, their Lite and Basic variants, External Vendors). It is a role membership, not a connection, resolved from {pcloud_source}.'
        + (
            ' With the vault validation the user must also exist in the vault (PCloud user management, matched by username, case insensitive), '
            'which happens when the user first goes to PrivCloud, so users that only hold a role are not counted.'
            if validate_pcloud_vault
            else ' The users are not checked against the vault (the check was turned off with --no-validate-pcloud-vault).'
        ),
    }


def _product_source(product: str, options: Dict[str, bool]) -> str:
    """The 'Counted from' text of a product, PrivCloud also mentions the vault validation when it was done"""
    return VAULT_VALIDATED_SOURCE if product == PCLOUD and options['validate_pcloud_vault'] else PRODUCT_SOURCES[product]


def _describe_group(products: frozenset) -> str:
    ordered = [p for p in (SCA, ZSP, PCLOUD) if p in products]
    others = [p for p in (SCA, ZSP, PCLOUD) if p not in products]
    if len(ordered) == 3:
        return 'Users that used all three products: SCA, SIA ZSP and PrivCloud.'
    if len(ordered) == 2:
        return f'Users that used {ordered[0]} and {ordered[1]}, but not {others[0]}.'
    return f'Users that used only {ordered[0]}, neither {others[0]} nor {others[1]}.'


def _methodology(report_options: Dict[str, bool]) -> List[str]:
    lines = [
        'Scope: the users of one tenant. Only users that exist in the Identity directory (suspended users included) are counted. '
        'Usernames that show up in sessions or roles but are not in Identity are not counted and are dropped.',
        'Usage: SCA and SIA ZSP are counted from session monitoring, a user used the product when it connected at least once in the '
        'timeframe. Failed sessions are ignored. PrivCloud is counted from the membership of the PrivCloud human roles.',
        'Groups: every user that used at least one product is placed in exactly one of the 7 groups, by the exact combination of products '
        'it used. The groups are mutually exclusive, so their counts add up to the total unique users.',
        'Usernames are compared case-insensitively.',
    ]
    if report_options['active_only']:
        lines.append(
            'Active users only: users whose account state is Locked, Disabled or Expired were taken out of every product before the '
            'groups were computed, and are reported separately.'
        )
    else:
        lines.append(
            'Account state is not checked, users that are Locked, Disabled or Expired are counted (use --active-only to leave them out).'
        )
    if report_options['validate_pcloud_vault']:
        lines.append(
            'Vault validation: a PrivCloud user is counted only when it also exists in the vault (PCloud user management). A user is '
            'provisioned to the vault automatically the first time it actually goes to PrivCloud, so users that only hold a role are left out.'
        )
    else:
        lines.append(
            'The PrivCloud users are not checked against the vault, so users that hold a role but never went to PrivCloud are counted '
            '(the vault validation was turned off with --no-validate-pcloud-vault, it is on by default).'
        )
    if report_options['identity_only']:
        lines.append(
            'Identity only mode: session monitoring was skipped, so only PrivCloud and the Identity data are reported, without groups.'
        )
    if not report_options['include_usernames']:
        lines.append('Usernames are not included in this report (use --include-usernames to add them), only counts.')
    return lines


def _users_entry(users: List[str], include_usernames: bool) -> dict:
    entry: dict = {'count': len(users)}
    if include_usernames:
        entry['users'] = users
    return entry


def build_report(
    usage: Usage,
    identity_users: Dict[str, str],
    groups: Optional[Dict[str, List[str]]],
    start: Optional[str],
    end: Optional[str],
    identity_only: bool = False,
    active_only: bool = False,
    directories: Optional[List[Dict[str, str]]] = None,
    federations: Optional[List[Dict[str, str]]] = None,
    include_usernames: bool = False,
    pcloud_by_user_roles: bool = False,
    validate_pcloud_vault: bool = False,
) -> dict:
    options = {
        'identity_only': identity_only,
        'active_only': active_only,
        'pcloud_by_user_roles': pcloud_by_user_roles,
        'validate_pcloud_vault': validate_pcloud_vault,
        'include_usernames': include_usernames,
    }
    dropped = {PCLOUD: sorted(usage.pcloud - identity_users.keys())}
    per_product = {PCLOUD: len(usage.pcloud & identity_users.keys())}
    if not identity_only:
        dropped[SCA] = sorted(usage.sca - identity_users.keys())
        dropped[ZSP] = sorted(usage.zsp - identity_users.keys())
        per_product = {
            SCA: len(usage.sca & identity_users.keys()),
            ZSP: len(usage.zsp & identity_users.keys()),
            PCLOUD: per_product[PCLOUD],
        }
    notes = list(usage.notes)
    for label, names in (
        ('The roles of {n} users could not be resolved, PrivCloud may be under-counted', usage.role_lookup_failed),
        ('The state of {n} users could not be read, they were kept as active', usage.state_lookup_failed),
    ):
        if names:
            notes.append(label.format(n=len(names)) + (f': {sorted(names)}' if include_usernames else ''))

    report: dict = {
        'mode': 'identity_only' if identity_only else 'full',
        'generated_at': _fmt_time(datetime.now(timezone.utc)),
        'options': options,
        'explanations': {
            'methodology': _methodology(options),
            'products': {
                name: text
                for name, text in _product_descriptions(pcloud_by_user_roles, validate_pcloud_vault).items()
                if name in per_product
            },
            'groups': {name: _describe_group(products) for name, products in GROUPS.items()} if not identity_only else {},
        },
        'directories': directories or [],
        'federations': federations or [],
        'identity_users_count': len(identity_users),
        'per_product_unique_users': per_product,
        'stats': usage.stats,
        'notes': notes,
        'dropped_not_in_identity': {product: _users_entry(users, include_usernames) for product, users in dropped.items()},
    }
    if not pcloud_by_user_roles:
        # resolved through the user roles the groups are irrelevant, the users are found whatever the way they hold the role
        report['pcloud_role_groups'] = usage.pcloud_groups
    if identity_only:
        report['pcloud_users'] = _users_entry(
            sorted((identity_users[u] for u in usage.pcloud & identity_users.keys()), key=str.lower), include_usernames
        )
    else:
        report['timeframe'] = {'start': start, 'end': end}
        report['groups'] = {
            name: {
                'description': _describe_group(GROUPS[name]),
                'products': [p for p in (SCA, ZSP, PCLOUD) if p in GROUPS[name]],
                **_users_entry(users, include_usernames),
            }
            for name, users in (groups or {}).items()
        }
        report['total_unique_users'] = sum(len(u) for u in (groups or {}).values())
    if validate_pcloud_vault:
        report['excluded_not_in_vault'] = _users_entry(
            sorted((identity_users[u] for u in usage.not_in_vault), key=str.lower), include_usernames
        )
    if active_only:
        report['excluded_inactive_users'] = {}
        for product, entries in usage.excluded_inactive.items():
            by_state: Dict[str, int] = {}
            for entry in entries:
                by_state[entry['state']] = by_state.get(entry['state'], 0) + 1
            excluded: dict = {'count': len(entries), 'by_state': by_state}
            if include_usernames:
                excluded['users'] = entries
            report['excluded_inactive_users'][product] = excluded
    return report


def _share(count: int, total: int) -> float:
    return count / total if total else 0.0


def write_excel(report: dict, path: str) -> None:
    try:
        from openpyxl import Workbook  # pylint: disable=import-outside-toplevel
        from openpyxl.styles import Alignment, Border, Font, PatternFill, Side  # pylint: disable=import-outside-toplevel
        from openpyxl.utils import get_column_letter  # pylint: disable=import-outside-toplevel
    except ImportError as ex:
        raise RuntimeError('Excel output requires openpyxl, run: pip install openpyxl') from ex

    header_fill = PatternFill('solid', fgColor='1F3864')
    band_fill = PatternFill('solid', fgColor='EEF3FA')
    total_fill = PatternFill('solid', fgColor='D9E2F3')
    border = Border(*(Side(style='thin', color='BFBFBF') for _ in range(4)))
    wrap_top = Alignment(wrap_text=True, vertical='top')

    def _title(sheet, title: str, description: Optional[str], width: int) -> int:
        sheet['A1'] = title
        sheet['A1'].font = Font(size=16, bold=True, color='1F3864')
        sheet.row_dimensions[1].height = 26
        next_row = 2
        if description:
            sheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=width)
            sheet['A2'] = description
            sheet['A2'].font = Font(italic=True, color='595959')
            sheet['A2'].alignment = wrap_top
            sheet.row_dimensions[2].height = 15 * max(1, len(description) // 110 + 1)
            next_row = 3
        return next_row + 1

    def _table(
        sheet, row: int, headers: List[str], rows: List[list], total_row: bool = False, percent_cols: tuple = (), wrap_cols: tuple = ()
    ) -> int:
        for col, header in enumerate(headers, 1):
            cell = sheet.cell(row=row, column=col, value=header)
            cell.font = Font(bold=True, color='FFFFFF')
            cell.fill = header_fill
            cell.border = border
            cell.alignment = Alignment(vertical='center', wrap_text=True)
        for index, values in enumerate(rows):
            is_total = total_row and index == len(rows) - 1
            for col, value in enumerate(values, 1):
                cell = sheet.cell(row=row + 1 + index, column=col, value=value)
                cell.border = border
                cell.alignment = wrap_top if col in wrap_cols else Alignment(vertical='top')
                if col in percent_cols:
                    cell.number_format = '0.0%'
                if is_total:
                    cell.font = Font(bold=True)
                    cell.fill = total_fill
                elif index % 2:
                    cell.fill = band_fill
        return row + len(rows) + 2

    def _widths(sheet, widths: List[int]) -> None:
        for col, width in enumerate(widths, 1):
            sheet.column_dimensions[get_column_letter(col)].width = width

    def _table_sheet(name: str, color: str, title: str, description: str, headers: List[str], rows: List[list], widths: List[int]) -> None:
        sheet = wb.create_sheet(name[:31])
        sheet.sheet_properties.tabColor = color
        header_row = _title(sheet, title, description, len(headers))
        end_row = _table(sheet, header_row, headers, rows) - 2
        _widths(sheet, widths)
        sheet.freeze_panes = sheet.cell(row=header_row + 1, column=1)
        if rows:
            sheet.auto_filter.ref = f'A{header_row}:{get_column_letter(len(headers))}{end_row}'

    wb = Workbook()
    summary = wb.active
    summary.title = 'Summary'
    summary.sheet_properties.tabColor = '1F3864'
    options = report['options']
    identity_total = report['identity_users_count']
    subtitle = f"Generated {report['generated_at']}"
    if 'timeframe' in report:
        subtitle = f"Timeframe {report['timeframe']['start']} - {report['timeframe']['end']}.  {subtitle}"
    row = _title(summary, 'License consumption report', subtitle, 5)
    if 'groups' in report:
        summary.cell(row=row - 1, column=1, value='Consumption by group').font = Font(bold=True, size=12)
        total = report['total_unique_users']
        group_rows = [
            [name, ' + '.join(data['products']), data['count'], _share(data['count'], total), data['description']]
            for name, data in report['groups'].items()
        ]
        group_rows.append(
            ['Total unique users', '', total, 1.0 if total else 0.0, 'Users that used at least one product, each counted once.']
        )
        row = _table(summary, row, ['Group', 'Products used', 'Users', 'Share of total', 'What it means'], group_rows, True, (4,), (5,))
    summary.cell(row=row, column=1, value='Per product').font = Font(bold=True, size=12)
    product_rows = [
        [product, _product_source(product, options), count, _share(count, identity_total), report['explanations']['products'][product]]
        for product, count in report['per_product_unique_users'].items()
    ]
    row = _table(
        summary,
        row + 1,
        ['Product', 'Counted from', 'Unique users', 'Share of Identity users', 'How it is counted'],
        product_rows,
        False,
        (4,),
        (5,),
    )
    if report['notes']:
        summary.cell(row=row, column=1, value='Notes').font = Font(bold=True, size=12)
        for offset, note in enumerate(report['notes'], 1):
            summary.merge_cells(start_row=row + offset, start_column=1, end_row=row + offset, end_column=5)
            cell = summary.cell(row=row + offset, column=1, value=note)
            cell.alignment = wrap_top
            summary.row_dimensions[row + offset].height = 15 * max(1, len(note) // 150 + 1)
    _widths(summary, [34, 30, 14, 18, 95])

    status = {True: 'yes', False: 'no'}
    info_rows = [
        [
            'Mode',
            'identity only' if options['identity_only'] else 'full',
            'Identity only skips session monitoring, so SCA, SIA ZSP and the groups are not calculated.',
        ],
        [
            'Identity users',
            identity_total,
            'Every user in the Identity directory, suspended users included. This is the base for the shares.',
        ],
        [
            'Active users only',
            status[options['active_only']],
            'When yes, Locked / Disabled / Expired users are taken out of the counts and listed below.',
        ],
        [
            'PrivCloud resolved from user roles',
            status[options['pcloud_by_user_roles']],
            'When yes, the roles of each user are read instead of the members of each role, which also counts users that hold a role through a group.',
        ],
        [
            'Validate PrivCloud in the vault',
            status[options['validate_pcloud_vault']],
            'When yes, a PrivCloud user is counted only when it exists in the vault, users are provisioned there when they first go to PrivCloud.',
        ],
        ['Usernames included', status[options['include_usernames']], 'When no, the report holds only counts, no usernames.'],
    ]
    if 'excluded_not_in_vault' in report:
        info_rows.append(
            [
                'Not in vault - PrivCloud',
                report['excluded_not_in_vault']['count'],
                'Users that hold a PrivCloud role but were never provisioned to the vault, so they are not counted.',
            ]
        )
    for product, data in report.get('excluded_inactive_users', {}).items():
        states = ', '.join(f'{state}: {count}' for state, count in data['by_state'].items()) or '-'
        info_rows.append(
            [
                f'Excluded inactive - {product}',
                data['count'],
                f'Users with a Locked / Disabled / Expired account that used {product} and were left out ({states}).',
            ]
        )
    for product, data in report['dropped_not_in_identity'].items():
        info_rows.append(
            [
                f'Not in Identity - {product}',
                data['count'],
                f'Usernames that used {product} but are not Identity users any more. They are not counted.',
            ]
        )
    for key, value in report['stats'].items():
        info_rows.append([key.replace('_', ' ').capitalize(), value, STAT_EXPLANATIONS.get(key, '')])
    _table_sheet(
        'Run info',
        '2E75B6',
        'Run information',
        'The options of this run and the numbers behind the totals.',
        ['Item', 'Value', 'Explanation'],
        info_rows,
        [40, 18, 110],
    )
    wb['Run info'].column_dimensions['C'].width = 110
    for cells in wb['Run info'].iter_rows(min_row=4, min_col=3, max_col=3):
        for cell in cells:
            cell.alignment = wrap_top

    how = wb.create_sheet('How it works')
    how.sheet_properties.tabColor = '2E75B6'
    first = _title(how, 'How the numbers are calculated', None, 2)
    for number, line in enumerate(report['explanations']['methodology'], 1):
        how.cell(row=first + number - 1, column=1, value=number).alignment = Alignment(vertical='top', horizontal='center')
        cell = how.cell(row=first + number - 1, column=2, value=line)
        cell.alignment = wrap_top
        how.row_dimensions[first + number - 1].height = 15 * max(1, len(line) // 120 + 1)
    _widths(how, [6, 130])

    if options['include_usernames']:
        if 'groups' in report:
            rows = [
                [user, name] + ['yes' if p in GROUPS[name] else '' for p in (SCA, ZSP, PCLOUD)]
                for name, data in report['groups'].items()
                for user in data['users']
            ]
            _table_sheet(
                'Users',
                '70AD47',
                'Users by group',
                'Every counted user with the group it landed in and the products it used.',
                ['Username', 'Group', SCA, ZSP, PCLOUD],
                rows,
                [48, 30, 10, 10, 12],
            )
        else:
            rows = [[user, 'yes'] for user in report['pcloud_users']['users']]
            _table_sheet(
                'Users',
                '70AD47',
                'PrivCloud users',
                'Identity users that hold a PrivCloud human role.',
                ['Username', PCLOUD],
                rows,
                [48, 12],
            )
    _table_sheet(
        'Directories',
        'A5A5A5',
        'Identity directories',
        'The directories of the tenant, a user can come from any of them.',
        ['Type', 'Name', 'Config', 'Directory service id'],
        [[d['type'], d['name'], d['config'], d['directory_service_uuid']] for d in report['directories']],
        [14, 34, 34, 42],
    )
    _table_sheet(
        'Federations',
        'A5A5A5',
        'External identity providers',
        'The SAML 2.0 / OIDC federations of the tenant, users can sign in through them.',
        ['Name', 'Type', 'Active', 'Domains', 'Federation id'],
        [[f['name'], f['type'], f['active'], f['domains'], f['federation_id']] for f in report['federations']],
        [34, 12, 10, 44, 40],
    )
    if 'pcloud_role_groups' in report:
        _table_sheet(
            'PrivCloud role groups',
            'FFC000',
            'Groups inside PrivCloud roles',
            'Groups that are members of the PrivCloud roles and could not be expanded to users, so the users that hold a role only through them are not counted '
            'unless the run used --pcloud-by-user-roles.',
            ['Role', 'Nested role', 'Group', 'Group id', 'Directory type', 'Directory'],
            [
                [e['role'], e['nested_role'], e['group_name'], e['group_id'], e['directory_type'], e['directory_name']]
                for e in report['pcloud_role_groups']
            ],
            [34, 30, 34, 40, 16, 30],
        )
    if options['include_usernames']:
        if 'excluded_not_in_vault' in report:
            _table_sheet(
                'Not in vault',
                'C00000',
                'PrivCloud role holders not in the vault',
                'Users that hold a PrivCloud role but were never provisioned to the vault (they never went to PrivCloud), so they were not counted.',
                ['Username'],
                [[user] for user in report['excluded_not_in_vault']['users']],
                [48],
            )
        if 'excluded_inactive_users' in report:
            _table_sheet(
                'Excluded (inactive)',
                'C00000',
                'Excluded inactive users',
                'Users that used a product but whose account is Locked, Disabled or Expired, so they were not counted.',
                ['Product', 'Username', 'State'],
                [
                    [product, user['username'], user['state']]
                    for product, data in report['excluded_inactive_users'].items()
                    for user in data['users']
                ],
                [14, 48, 14],
            )
        _table_sheet(
            'Not in Identity',
            'C00000',
            'Users not in Identity',
            'Usernames that used a product but are not Identity users, they are not counted.',
            ['Product', 'Username'],
            [[product, user] for product, data in report['dropped_not_in_identity'].items() for user in data['users']],
            [14, 48],
        )
    wb.save(path)


def print_report(report: dict) -> None:
    options = report['options']
    line = '=' * 100
    print(f'\n{line}\nLICENSE CONSUMPTION REPORT  ({report["generated_at"]})\n{line}')
    if 'timeframe' in report:
        print(f"Timeframe: {report['timeframe']['start']} - {report['timeframe']['end']}")
    print(
        f"Mode: {report['mode']}   active only: {options['active_only']}   vault validation: {options['validate_pcloud_vault']}   "
        f"usernames included: {options['include_usernames']}"
    )
    print('\nHow the numbers are calculated:')
    for number, text in enumerate(report['explanations']['methodology'], 1):
        print(f'  {number}. {text}')

    print(f"\nIdentity users: {report['identity_users_count']}  (every user of the directory, suspended included)")
    print('\nPer product unique users (Identity users only):')
    for product, count in report['per_product_unique_users'].items():
        print(f'  {product}: {count}\n      {report["explanations"]["products"][product]}')

    if 'groups' in report:
        print('\nConsumption by group (each user is in exactly one group):')
        for name, data in report['groups'].items():
            print(f"  {name}: {data['count']}\n      {data['description']}")
            for user in data.get('users', []):
                print(f'      - {user}')
        print(f"\nTotal unique users: {report['total_unique_users']}  (users that used at least one product)")
    else:
        pcloud_users = report['pcloud_users']
        print(f"\nPrivCloud users: {pcloud_users['count']}")
        for user in pcloud_users.get('users', []):
            print(f'  - {user}')

    if 'excluded_not_in_vault' in report:
        not_in_vault = report['excluded_not_in_vault']
        print(f"\nPrivCloud role holders not in the vault: {not_in_vault['count']}  (never provisioned to the vault, not counted)")
        for user in not_in_vault.get('users', []):
            print(f'  - {user}')
    for product, data in report.get('excluded_inactive_users', {}).items():
        print(
            f"\nExcluded inactive users of {product}: {data['count']} {data['by_state'] or ''}  (account Locked / Disabled / Expired, not counted)"
        )
        for user in data.get('users', []):
            print(f"  - {user['username']} ({user['state']})")
    print('\nNot in Identity (not counted):')
    for product, data in report['dropped_not_in_identity'].items():
        print(f"  {product}: {data['count']}")
        for user in data.get('users', []):
            print(f'      - {user}')

    if 'pcloud_role_groups' in report:
        print(f"\nGroups as PrivCloud role members (not expanded to users): {len(report['pcloud_role_groups'])}")
        for entry in report['pcloud_role_groups']:
            print(f"  [{entry['role']}] {entry['group_name']} - {entry['directory_type']} ({entry['directory_name']})")
    print(f"\nFederations (external identity providers): {len(report['federations'])}")
    for federation in report['federations']:
        print(f"  {federation['name']} - {federation['type']} - active: {federation['active']} - domains: {federation['domains']}")
    print(f"\nDirectories: {len(report['directories'])}")
    for directory in report['directories']:
        print(f"  {directory['type']} - {directory['name'] or directory['config']} [{directory['directory_service_uuid']}]")
    for note in report['notes']:
        print(f'NOTE: {note}')
    print(line)


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    """Timeframe, output and logging arguments shared with the system user variant"""
    parser.add_argument('--start', help=f'Timeframe start, UTC ISO (default: {DEFAULT_LOOKBACK_DAYS} days before --end)')
    parser.add_argument('--end', help='Timeframe end, UTC ISO (default: now)')
    parser.add_argument('--output-dir', default='.', help='Where to write the json and xlsx files')
    parser.add_argument(
        '--pcloud-by-user-roles',
        action=argparse.BooleanOptionalAction,
        default=True,
        help='Resolve PrivCloud users from the roles of each Identity user instead of from the role members, '
        'to count users that are in the roles only through groups (default: on, use --no-pcloud-by-user-roles to turn off)',
    )
    parser.add_argument(
        '--max-workers', type=int, default=DEFAULT_MAX_WORKERS, help='Parallel per user lookups (--pcloud-by-user-roles, --active-only)'
    )
    parser.add_argument(
        '--validate-pcloud-vault',
        action=argparse.BooleanOptionalAction,
        default=True,
        help='Count a PrivCloud user only when it also exists in the vault (PCloud user management). Users are provisioned to the '
        'vault when they first go to PrivCloud, so this leaves out users that only hold a role. Needs the right to list vault users '
        '(default: on, use --no-validate-pcloud-vault to turn off)',
    )
    parser.add_argument(
        '--vault-page-size',
        type=int,
        default=DEFAULT_VAULT_PAGE_SIZE,
        help='Vault users requested per call with --validate-pcloud-vault, smaller pages avoid the timeouts of a big vault',
    )
    parser.add_argument(
        '--sessions-workers',
        type=int,
        default=DEFAULT_SESSIONS_WORKERS,
        help='Parallel session monitoring requests, the timeframe is fetched as day windows (SCA and SIA ZSP)',
    )
    parser.add_argument(
        '--sessions-page-size',
        type=int,
        default=DEFAULT_SESSIONS_PAGE_SIZE,
        help='Sessions requested per call to session monitoring, 0 uses the service default page size. '
        'A page size the API does not accept is dropped automatically',
    )
    parser.add_argument(
        '--include-usernames',
        action='store_true',
        help='Also save and print the usernames (per group, not in Identity, excluded inactive), without it only counts are reported',
    )
    parser.add_argument(
        '--active-only',
        action=argparse.BooleanOptionalAction,
        default=True,
        help='Count only users with an active account, users that are Locked / Disabled / Expired are left out and listed separately '
        '(default: on, use --no-active-only to turn off)',
    )
    parser.add_argument(
        '--identity-only',
        action='store_true',
        help='Only calculate the Identity side (Identity users and PrivCloud role members), skipping session monitoring and the groups',
    )
    parser.add_argument(
        '--log-level',
        default='ERROR',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Script log level, logs go to stderr (SDK internal logs stay quiet unless the LOG_LEVEL env variable is set)',
    )


def setup_and_resolve_timeframe(parser: argparse.ArgumentParser, args: argparse.Namespace) -> tuple:
    """Configures the logger and returns the (start, end) timeframe of the parsed common arguments"""
    get_logger(LOGGER_NAME, logging.getLevelName(args.log_level))
    # the SDK builds a random browser user agent per client, and fake_useragent warns when it falls back to its built in data
    logging.getLogger('fake_useragent').setLevel(logging.ERROR)
    end = _parse_time(args.end) if args.end else datetime.now(timezone.utc).replace(microsecond=0)
    start = _parse_time(args.start) if args.start else end - timedelta(days=DEFAULT_LOOKBACK_DAYS)
    if start >= end:
        parser.error('--start must be before --end')
    return start, end


def run_analytics(
    isp_auth: ArkISPAuth,
    start: datetime,
    end: datetime,
    output_dir: str,
    identity_only: bool = False,
    pcloud_by_user_roles: bool = False,
    max_workers: int = DEFAULT_MAX_WORKERS,
    active_only: bool = False,
    include_usernames: bool = False,
    sessions_workers: int = DEFAULT_SESSIONS_WORKERS,
    sessions_page_size: Optional[int] = DEFAULT_SESSIONS_PAGE_SIZE,
    validate_pcloud_vault: bool = False,
    vault_page_size: int = DEFAULT_VAULT_PAGE_SIZE,
) -> None:
    """Runs the steps with an authenticated ISP auth and writes the stdout / json / excel output, identity only skips sessions"""
    usage = Usage()
    total_steps = (2 if identity_only else 4) + int(active_only)
    logger.info(f'Step 1/{total_steps}: collecting identity users')
    user_ids: Dict[str, str] = {}
    directories = collect_directories(isp_auth)
    federations = collect_federations(isp_auth)
    identity_users = collect_identity_users(isp_auth, user_ids)
    if pcloud_by_user_roles:
        logger.info(f'Step 2/{total_steps}: collecting PrivCloud users by the roles of each identity user')
        collect_pcloud_users_by_user_roles(isp_auth, usage, user_ids, max_workers)
    else:
        logger.info(f'Step 2/{total_steps}: collecting PrivCloud users by human roles')
        collect_pcloud_users(isp_auth, usage)
    logger.info(f'PrivCloud unique role members: [{len(usage.pcloud)}]')
    if validate_pcloud_vault:
        logger.info('Validating that the PrivCloud users exist in the vault')
        validate_pcloud_in_vault(isp_auth, usage, identity_users, vault_page_size)
    groups = None
    if identity_only:
        logger.info('Identity only mode, skipping session monitoring and the groups calculation')
    else:
        logger.info(f'Step 3/{total_steps}: collecting SIA ZSP / SCA users by session monitoring')
        collect_session_users(isp_auth, start, end, usage, sessions_workers, sessions_page_size)
        if active_only:
            logger.info(f'Step 4/{total_steps}: excluding inactive users')
            exclude_inactive_users(isp_auth, usage, identity_users, user_ids, max_workers)
        logger.info(f'Step {total_steps}/{total_steps}: computing groups')
        groups = compute_groups(usage, identity_users)
    if identity_only and active_only:
        logger.info(f'Step 3/{total_steps}: excluding inactive users')
        exclude_inactive_users(isp_auth, usage, identity_users, user_ids, max_workers)
    report = build_report(
        usage,
        identity_users,
        groups,
        _fmt_time(start),
        _fmt_time(end),
        identity_only,
        active_only,
        directories,
        federations,
        include_usernames,
        pcloud_by_user_roles,
        validate_pcloud_vault,
    )

    os.makedirs(output_dir, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    prefix = 'license_consumption_identity' if identity_only else 'license_consumption'
    json_path = os.path.join(output_dir, f'{prefix}_{stamp}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print_report(report)
    logger.info(f'JSON written to {json_path}')
    xlsx_path = os.path.join(output_dir, f'{prefix}_{stamp}.xlsx')
    write_excel(report, xlsx_path)
    logger.info(f'Excel written to {xlsx_path}')


def run_analytics_from_args(isp_auth: ArkISPAuth, start: datetime, end: datetime, args: argparse.Namespace) -> None:
    """Runs the analytics with the options of the common arguments"""
    run_analytics(
        isp_auth,
        start,
        end,
        args.output_dir,
        identity_only=args.identity_only,
        pcloud_by_user_roles=args.pcloud_by_user_roles,
        max_workers=args.max_workers,
        active_only=args.active_only,
        include_usernames=args.include_usernames,
        sessions_workers=args.sessions_workers,
        sessions_page_size=args.sessions_page_size,
        validate_pcloud_vault=args.validate_pcloud_vault,
        vault_page_size=args.vault_page_size,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description='SCA / SIA ZSP / PrivCloud license consumption analytics')
    parser.add_argument('--username', required=True, help='Tenant user to authenticate with')
    parser.add_argument('--secret', help='Secret / password of the user (default: ARK_SECRET env)')
    parser.add_argument('--service-user', action='store_true', help='Authenticate as an Identity service user instead of a regular user')
    add_common_arguments(parser)
    args = parser.parse_args()
    start, end = setup_and_resolve_timeframe(parser, args)

    secret = args.secret or os.environ.get('ARK_SECRET')
    if not secret:
        parser.error('a secret is required, use --secret or the ARK_SECRET env variable')
    logger.info(
        f'Starting license consumption analytics for [{args.username}] ({"service user" if args.service_user else "user"}), '
        f'timeframe [{_fmt_time(start)}] - [{_fmt_time(end)}]'
    )
    isp_auth = ArkISPAuth(cache_authentication=False)
    isp_auth.authenticate(
        auth_profile=ArkAuthProfile(
            username=args.username,
            auth_method=ArkAuthMethod.IdentityServiceUser if args.service_user else ArkAuthMethod.Identity,
            auth_method_settings=(IdentityServiceUserArkAuthMethodSettings() if args.service_user else IdentityArkAuthMethodSettings()),
        ),
        secret=ArkSecret(secret=secret),
    )
    logger.info('Authenticated successfully')
    run_analytics_from_args(isp_auth, start, end, args)


if __name__ == '__main__':
    main()
