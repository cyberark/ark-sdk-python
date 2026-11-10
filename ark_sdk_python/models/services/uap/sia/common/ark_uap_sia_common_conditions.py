from typing import Optional

from pydantic import Field
from typing_extensions import Annotated

from ark_sdk_python.models.services.uap.common import ArkUAPConditions


class ArkUAPSIACommonConditions(ArkUAPConditions):
    idle_time: Annotated[
        Optional[int],
        Field(
            gt=0,
            le=120,
            default=10,
            description='The maximum idle time before the session ends, in minutes.',
        ),
    ]
    override_idle_time: Annotated[
        Optional[bool],
        Field(
            default=None,
            description='When true, the policy idle_time overrides the tenant-level default idle time setting.',
        ),
    ] = None
    override_max_session_duration: Annotated[
        Optional[bool],
        Field(
            default=None,
            description='When true, the policy max_session_duration overrides the tenant-level default maximum session duration.',
        ),
    ] = None
