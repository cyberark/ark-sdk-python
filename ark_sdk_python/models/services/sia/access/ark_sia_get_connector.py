from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIAGetConnector(ArkModel):
    connector_id: str = Field(description='The id of the connector to get')
