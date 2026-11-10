from pydantic import Field

from ark_sdk_python.models import ArkPollableModel


class ArkCmgrUpgradeConnector(ArkPollableModel):
    connector_id: str = Field(description='Connector id to upgrade')
