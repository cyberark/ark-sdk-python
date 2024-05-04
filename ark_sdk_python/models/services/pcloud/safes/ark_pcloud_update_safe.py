from pydantic import Field

from ark_sdk_python.models.services.pcloud.safes.ark_pcloud_safe import ArkPCloudBaseSafe


class ArkPCloudUpdateSafe(ArkPCloudBaseSafe):
    safe_id: str = Field(description='Safe id to update')
