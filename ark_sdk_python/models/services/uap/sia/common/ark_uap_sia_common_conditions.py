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
