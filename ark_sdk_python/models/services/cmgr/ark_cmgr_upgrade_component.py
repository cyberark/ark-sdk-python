from pydantic import Field

from ark_sdk_python.models import ArkPollableModel


class ArkCmgrUpgradeComponent(ArkPollableModel):
    connector_id: str = Field(description='Connector id to upgrade a component from')
    component_id: str = Field(description='Component id to upgrade')
    component_version: str = Field(description='Which version to upgrade to', default='latest')
