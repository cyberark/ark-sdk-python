from pydantic import Field

from ark_sdk_python.models import ArkPollableModel


class ArkCmgrReinstallComponent(ArkPollableModel):
    connector_id: str = Field(description='Connector id to reinstall a component on')
    component_id: str = Field(description='Component id to reinstall')
