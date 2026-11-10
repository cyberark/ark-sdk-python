from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkCmgrConnectorSetupScript(ArkModel):
    script: str = Field(description='Bash script to install the connector with')
    script_url: str = Field(description='URL of the script to manually install')
