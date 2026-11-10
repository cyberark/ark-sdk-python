from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkSIARotateHttpsRelay(ArkModel):
    https_relay_id: str = Field(description='HTTPS relay to rotate certificate')
