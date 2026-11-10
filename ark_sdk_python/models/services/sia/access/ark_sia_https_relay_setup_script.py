from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIAHttpsRelaySetupScript(ArkModel):
    script_url: str = Field(description='URL to download the HTTPS relay setup script from')
    bash_cmd: str = Field(description='Bash command to execute for installing the HTTPS relay')
