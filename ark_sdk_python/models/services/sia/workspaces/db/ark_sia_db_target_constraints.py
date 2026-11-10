from typing import Final, List, Optional, Union

from pydantic import StringConstraints
from typing_extensions import Annotated

from ark_sdk_python.models.services.sia.workspaces.db.ark_sia_db_database_target_service import ArkSIADBDatabaseTargetService

TARGET_NAME_MAX_LENGTH: Final[int] = 256
TARGET_NORMAL_STR_MAX_LENGTH: Final[int] = 2048
TARGET_LONG_STR_MAX_LENGTH: Final[int] = 4096
TARGET_PORT_MIN: Final[int] = 1
TARGET_PORT_MAX: Final[int] = 65535
SECRET_ID_REGEX_PATTERN: Final[str] = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

ArkSIADBTargetName = Annotated[str, StringConstraints(min_length=1, max_length=TARGET_NAME_MAX_LENGTH)]
# The name of an already onboarded database, used to look it up instead of by id.
ArkSIADBTargetLookupName = Annotated[str, StringConstraints(max_length=TARGET_NAME_MAX_LENGTH)]
ArkSIADBTargetNormalStr = Annotated[str, StringConstraints(max_length=TARGET_NORMAL_STR_MAX_LENGTH)]
ArkSIADBTargetLongStr = Annotated[str, StringConstraints(max_length=TARGET_LONG_STR_MAX_LENGTH)]
ArkSIADBTargetNonEmptyEndpoint = Annotated[str, StringConstraints(min_length=1, max_length=TARGET_LONG_STR_MAX_LENGTH, pattern=r'^\S+$')]
ArkSIADBTargetEndpoint = Annotated[str, StringConstraints(max_length=TARGET_LONG_STR_MAX_LENGTH, pattern=r'^\S*$')]
ArkSIADBTargetSecretID = Annotated[str, StringConstraints(pattern=SECRET_ID_REGEX_PATTERN)]
# A service is either a plain service name or a service object, depending on the database family.
ArkSIADBTargetServiceTypes = Union[ArkSIADBTargetLongStr, ArkSIADBDatabaseTargetService]


def validate_no_surrounding_whitespace(value: Optional[str]) -> Optional[str]:
    if value is not None and value != value.strip():
        raise ValueError('Must not have leading or trailing whitespace')
    return value


def validate_services_no_surrounding_whitespace(services: Optional[List] = None) -> Optional[List]:
    # Service objects carry their name in a constrained field of their own, so only the plain
    # service names are checked here.
    for service in services or []:
        if isinstance(service, str):
            validate_no_surrounding_whitespace(service)
    return services
