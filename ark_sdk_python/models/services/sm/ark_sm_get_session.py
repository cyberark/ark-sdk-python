from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSMGetSession(ArkModel):
    session_id: str = Field(description='Session id to get')
