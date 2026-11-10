from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkCmgrGetConnectorComponent(ArkModel):
    connector_id: str = Field(description='ID of the connector to get the component from')
    component_id: str = Field(description='ID of the component to get')
