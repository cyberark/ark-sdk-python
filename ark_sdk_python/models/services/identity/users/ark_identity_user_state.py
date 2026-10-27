from typing import Final, Optional

from pydantic import Field, computed_field

from ark_sdk_python.models import ArkModel

ACTIVE_USER_STATE: Final[str] = 'None'  # identity reports a healthy account as state None, otherwise Locked / Disabled / Expired


class ArkIdentityUserState(ArkModel):
    user_id: str = Field(description='Id of the user')
    state: Optional[str] = Field(
        description='State of the user account, None means no restriction, or Locked / Disabled / Expired', default=None
    )

    @computed_field
    @property
    def is_active(self) -> bool:
        """Whether the account is usable, i.e. it is not locked, disabled or expired"""
        return self.state in (None, '', ACTIVE_USER_STATE)
