from pydantic import Field

from ark_sdk_python.models.services.dpa.db.ark_dpa_db_base_generate_assets import ArkDPADBBaseGenerateAssets


class ArkDPADBOracleGenerateAssets(ArkDPADBBaseGenerateAssets):
    folder: str = Field(description='Where to output the assets')
    unzip: bool = Field(description='Whether to save zipped or not', default=True)
