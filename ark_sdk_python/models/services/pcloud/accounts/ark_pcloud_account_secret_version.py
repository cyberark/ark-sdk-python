from datetime import datetime

from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkPCloudAccountSecretVersion(ArkCamelizedModel):
    is_temporary: bool = Field(description='Whether the secret is permenant or temporary')
    modification_date: datetime = Field(description='Modification time of the secret')
    modified_by: str = Field(description='Username who modified the secret')
    version_id: int = Field(description='Version id of the secret')
