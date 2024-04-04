from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityResetUserPassword(ArkModel):
    username: str = Field(description='Username to reset the password for')
    new_password: str = Field(description='New password to reset to')
