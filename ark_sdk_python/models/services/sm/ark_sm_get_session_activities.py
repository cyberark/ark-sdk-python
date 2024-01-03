from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSMGetSessionActivities(ArkModel):
    session_id: str = Field(description='Session id to get the activities for')
