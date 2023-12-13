from pydantic import HttpUrl

from ark_sdk_python.models import ArkModel


class IdentityEndpointResponse(ArkModel):
    endpoint: HttpUrl
