from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel


class ArkSIAGenerateShortenedConnectionString(ArkModel):
    raw_connection_string: str = Field(description='Raw connection string to shorten')
