from pydantic import Field

from ark_sdk_python.models import ArkCamelizedModel


class ArkSIAUpdateMaintenanceMode(ArkCamelizedModel):
    connector_id: str = Field(description='ID of the connector to update')
    maintenance: bool = Field(
        default=False,
        description='Enable maintenance mode when --maintenance is present; --no-maintenance or absence keeps it disabled',
    )
    retry_count: int = Field(
        default=10,
        alias='RetryCount',
        description='Number of retries for the maintenance mode update operation (internal use)',
        exclude=True,
    )
    retry_delay_seconds: int = Field(
        default=5,
        alias='RetryDelay',
        description='Delay in seconds between maintenance mode update retries (internal use)',
        exclude=True,
    )
