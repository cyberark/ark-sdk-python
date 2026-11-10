from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkCmgrListConnectorComponents(ArkModel):
    connector_id: str = Field(description='ID of the connector to list the components of')
