from typing import Optional

from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel


class ArkAccessAssetsListAssets(ArkModel):
    recents_only: bool = Field(description='Should return only recently-used assets', default=False)
    favorites_only: bool = Field(description='Should return only favorite assets', default=False)
    access_method: Optional[str] = Field(
        description='Filter infrastructure assets by access method', default=None, examples=['vaulted', 'zsp']
    )
    limit: Optional[int] = Field(
        ge=1,
        le=1000,
        default=None,
        description='This parameter sets the maximum number of the infrastructure items to be retrieved. '
        'The default value is 1000, the minimum limit is 1, and the maximum limit is 1000',
    )
    sort: Optional[str] = Field(
        description='This parameter sets the sorting order of the retrieved items.'
        ' The sorting order can be set to ascending or descending. '
        'The default value is ascending',
        default=None,
        examples=['address.asc', 'platformId.desc', 'lastAccessed.desc'],
    )
    search: Optional[str] = Field(
        description='This parameter is used to search for the assets based on specific criteria',
        default=None,
        examples=['address contains "1.2.3.4"'],
    )
