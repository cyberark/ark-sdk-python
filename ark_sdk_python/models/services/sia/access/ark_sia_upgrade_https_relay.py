from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIAUpgradeHttpsRelay(ArkModel):
    https_relay_id: str = Field(description='Https relay that being upgraded')
