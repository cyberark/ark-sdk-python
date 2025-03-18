from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIAConnectorSetupScript(ArkModel):
    script_url: str = Field(
        description='URL to manually download the SIA connector installation script. '
        'The script contains a secret token that is valid for 15 minutes from the time it is generated.'
    )
    bash_cmd: str = Field(
        description='Bash command to automatically download the installation script and run it on the connector host machine. '
        'The script contains a secret token that is valid for 15 minutes from the time it is generated.'
    )
