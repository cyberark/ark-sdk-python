from typing import List, Optional

from pydantic import Field, conint, constr

from ark_sdk_python.models import ArkCamelizedModel


class ArkUAPTimeCondition(ArkCamelizedModel):
    days_of_the_week: List[conint(ge=0, le=6)] = Field(
        description='The days that the policy will be active', default_factory=lambda: [0, 1, 2, 3, 4, 5, 6]
    )
    from_hour: Optional[constr(pattern=r'\w+')] = Field(description='the policy will be active from hour', default=None)
    to_hour: Optional[constr(pattern=r'\w+')] = Field(description='the policy will be active to time', default=None)
