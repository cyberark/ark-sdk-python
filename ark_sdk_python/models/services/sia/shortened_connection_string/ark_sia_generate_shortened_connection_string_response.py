from pydantic import Field

from ark_sdk_python.models.ark_model import ArkModel


class ArkSIAGenerateShortenedConnectionStringResponse(ArkModel):
    shortened_connection_string: str = Field(description='The generated shortened connection string', alias='connection_string_alias')
    raw_connection_string: str = Field(description='The original raw connection string from the request')
