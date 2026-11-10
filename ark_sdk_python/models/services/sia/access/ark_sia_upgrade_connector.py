from pydantic import Field

from ark_sdk_python.models import ArkPollableModel


class ArkSIAUpgradeConnector(ArkPollableModel):
    connector_id: str = Field(description='The id of the connector to upgrade')
