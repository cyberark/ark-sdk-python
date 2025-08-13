from typing import Any, Dict

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel


class ArkPCloudPlatformDetails(ArkCamelizedModel):
    """
    Model for Platform Details API response.
    This API endpoint returns a different structure than the List Platforms API.
    """

    platform_id: str = Field(description='Platform ID', alias='PlatformID')
    active: bool = Field(description='Whether platform is active', alias='Active')
    details: Dict[str, Any] = Field(description='Platform configuration details', alias='Details')
