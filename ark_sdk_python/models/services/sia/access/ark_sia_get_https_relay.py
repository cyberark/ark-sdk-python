from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIAGetHttpsRelay(ArkModel):
    https_relay_id: str = Field(description='Https relay id we would like to get information about')
