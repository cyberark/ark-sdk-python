from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkSMSessionActivitiesFilter(ArkCamelizedModel):
    session_id: str = Field(description='Session id to get')
    command_contains: str = Field(description='String which the command contains')
