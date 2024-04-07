from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityUserByName(ArkModel):
    username: str = Field(description='User name to find the id for')
