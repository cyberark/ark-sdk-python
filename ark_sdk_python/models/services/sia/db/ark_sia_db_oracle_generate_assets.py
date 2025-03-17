from pydantic import Field

from ark_sdk_python.models.services.sia.db.ark_sia_db_base_generate_assets import ArkSIADBBaseGenerateAssets


class ArkSIADBOracleGenerateAssets(ArkSIADBBaseGenerateAssets):
    unzip: bool = Field(description='Whether to save zipped or not', default=True)
    include_sso: bool = Field(description='Whether to generate the asset with SSO details', default=True)
