from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityUserById(ArkModel):
    user_id: str = Field(description='Id to find the user for')
