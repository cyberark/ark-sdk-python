from typing import Optional

from pydantic import Field

from ark_sdk_python.models import ArkModel


class ArkIdentityFederationsFilter(ArkModel):
    federation_name: Optional[str] = Field(description='Only return the federation with this display name', default=None)
    federation_type: Optional[str] = Field(description='Only return federations of this protocol, SAML 2.0 or OIDC', default=None)
