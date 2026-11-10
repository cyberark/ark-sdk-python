from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkCmgrRescanComponents(ArkModel):
    connector_id: str = Field(description='ID of the connector to rescan components on')
