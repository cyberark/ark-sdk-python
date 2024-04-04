from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityUserIdByName(ArkModel):
    username: str = Field(description='User name to find the id for')
