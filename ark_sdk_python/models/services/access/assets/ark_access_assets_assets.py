from typing import List

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkCamelizedModel
from ark_sdk_python.models.services.access.assets.ark_access_assets_asset import ArkAccessAssetsAsset


class ArkAccessAssetsAssets(ArkCamelizedModel):
    assets: List[ArkAccessAssetsAsset] = Field(
        description='List of the end-user assets.',
        default_factory=list,
        validation_alias='targets',
    )
    size: int = Field(description='The total number of assets')
