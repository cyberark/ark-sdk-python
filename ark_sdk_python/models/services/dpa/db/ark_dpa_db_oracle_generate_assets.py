from pydantic import Field

from ark_sdk_python.models.services.dpa.db.ark_dpa_db_base_generate_assets import ArkDPADBBaseGenerateAssets


class ArkDPADBOracleGenerateAssets(ArkDPADBBaseGenerateAssets):
    unzip: bool = Field(description='Whether to save zipped or not', default=True)
    include_sso: bool = Field(description='Whether to generate the asset with SSO details', default=True)
