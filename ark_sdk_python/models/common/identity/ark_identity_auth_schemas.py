from typing import Dict, List, Optional

from pydantic import Field, StringConstraints
from typing_extensions import Annotated

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.common.identity.ark_identity_common_schemas import IdentityApiResponse


class PodFqdnResult(ArkModel):
    pod_fqdn: Annotated[str, StringConstraints(min_length=2)] = Field(alias='PodFqdn')


class AdvanceAuthResult(ArkModel):
    display_name: Optional[Annotated[str, StringConstraints(min_length=2)]] = Field(default=None, alias='DisplayName')
    auth: Annotated[str, StringConstraints(min_length=2)] = Field(alias='Auth')
    summary: Annotated[str, StringConstraints(min_length=2)] = Field(alias='Summary')
    token: Optional[Annotated[str, StringConstraints(min_length=2)]] = Field(default=None, alias='Token')
    refresh_token: Optional[Annotated[str, StringConstraints(min_length=2)]] = Field(default=None, alias='RefreshToken')
    token_lifetime: Optional[int] = Field(default=None, alias='TokenLifetime')
    customer_id: Optional[str] = Field(default=None, alias='CustomerID')
    user_id: Optional[str] = Field(default=None, alias='UserId')
    pod_fqdn: Optional[str] = Field(default=None, alias='PodFqdn')


class Mechanism(ArkModel):
    answer_type: Annotated[str, StringConstraints(min_length=2)] = Field(alias='AnswerType')
    name: Annotated[str, StringConstraints(min_length=2)] = Field(alias='Name')
    prompt_mech_chosen: Annotated[str, StringConstraints(min_length=2)] = Field(alias='PromptMechChosen')
    prompt_select_mech: Optional[Annotated[str, StringConstraints(min_length=2)]] = Field(default=None, alias='PromptSelectMech')
    mechanism_id: Annotated[str, StringConstraints(min_length=2)] = Field(alias='MechanismId')
    image: Optional[str] = Field(alias='Image', default=None)


class Challenge(ArkModel):
    mechanisms: Annotated[List[Mechanism], Field(min_length=1)] = Field(alias='Mechanisms')


class AdvanceAuthMidResult(ArkModel):
    summary: Annotated[str, StringConstraints(min_length=2)] = Field(alias='Summary')
    generated_auth_value: Optional[str] = Field(default=None, alias='GeneratedAuthValue')
    challenges: Optional[Annotated[List[Challenge], Field(min_length=1)]] = Field(default=None, alias='Challenges')


class StartAuthResult(ArkModel):
    challenges: Optional[Annotated[List[Challenge], Field(min_length=1)]] = Field(default=None, alias='Challenges')
    session_id: Optional[Annotated[str, StringConstraints(min_length=2)]] = Field(default=None, alias='SessionId')
    idp_redirect_url: Optional[str] = Field(default=None, alias='IdpRedirectUrl')
    idp_login_session_id: Optional[str] = Field(default=None, alias='IdpLoginSessionId')
    idp_redirect_short_url: Optional[str] = Field(default=None, alias='IdpRedirectShortUrl')
    idp_short_url_id: Optional[str] = Field(default=None, alias='IdpShortUrlId')
    idp_oob_auth_pin_required: Optional[bool] = Field(default=None, alias='IdpOobAuthPinRequired')
    tenant_id: Optional[str] = Field(default=None, alias='TenantId')


class IdpAuthStatusResult(ArkModel):
    auth_level: Optional[str] = Field(default=None, alias='AuthLevel')
    display_name: Optional[str] = Field(default=None, alias='DisplayName')
    auth: Optional[str] = Field(default=None, alias='Auth')
    user_id: Optional[str] = Field(default=None, alias='UserId')
    state: Optional[str] = Field(default=None, alias='State')
    token_lifetime: Optional[int] = Field(default=None, alias='TokenLifetime')
    token: Optional[str] = Field(default=None, alias='Token')
    refresh_token: Optional[str] = Field(default=None, alias='RefreshToken')
    email_address: Optional[str] = Field(default=None, alias='EmailAddress')
    user_directory: Optional[str] = Field(default=None, alias='UserDirectory')
    pod_fqdn: Optional[str] = Field(default=None, alias='PodFqdn')
    user: Optional[str] = Field(default=None, alias='User')
    customer_id: Optional[str] = Field(default=None, alias='CustomerID')
    forest: Optional[str] = Field(default=None, alias='Forest')
    system_id: Optional[str] = Field(default=None, alias='SystemID')
    source_ds_type: Optional[str] = Field(default=None, alias='SourceDsType')
    summary: Optional[str] = Field(default=None, alias='Summary')


class TenantFqdnResponse(IdentityApiResponse):
    result: PodFqdnResult = Field(alias='Result')


class AdvanceAuthMidResponse(IdentityApiResponse):
    result: AdvanceAuthMidResult = Field(alias='Result')


class AdvanceAuthResponse(IdentityApiResponse):
    result: AdvanceAuthResult = Field(alias='Result')


class StartAuthResponse(IdentityApiResponse):
    result: StartAuthResult = Field(alias='Result')


class GetTenantSuffixResult(IdentityApiResponse):
    result: Optional[Dict] = Field(default=None, alias='Result')


class IdpAuthStatusResponse(IdentityApiResponse):
    result: IdpAuthStatusResult = Field(alias='Result')
