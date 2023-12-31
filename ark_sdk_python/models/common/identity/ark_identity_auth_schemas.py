from typing import Dict, Optional

from pydantic import Field, conlist, constr

from ark_sdk_python.models.ark_model import ArkModel
from ark_sdk_python.models.common.identity.ark_identity_common_schemas import IdentityApiResponse


class PodFqdnResult(ArkModel):
    pod_fqdn: constr(min_length=2) = Field(alias='PodFqdn')

    def get_tenant_id(self):
        return self.pod_fqdn.split('.')[0]


class AdvanceAuthResult(ArkModel):
    display_name: Optional[constr(min_length=2)] = Field(alias='DisplayName')
    auth: constr(min_length=2) = Field(alias='Auth')
    summary: constr(min_length=2) = Field(alias='Summary')
    token: Optional[constr(min_length=2)] = Field(alias='Token')
    refresh_token: Optional[constr(min_length=2)] = Field(alias='RefreshToken')
    token_lifetime: Optional[int] = Field(alias='TokenLifetime')
    customer_id: Optional[str] = Field(alias='CustomerID')
    user_id: Optional[str] = Field(alias='UserId')
    pod_fqdn: Optional[str] = Field(alias='PodFqdn')


class AdvanceAuthMidResult(ArkModel):
    summary: constr(min_length=2) = Field(alias='Summary')
    generated_auth_value: Optional[str] = Field(alias='GeneratedAuthValue')


class Mechanism(ArkModel):
    answer_type: constr(min_length=2) = Field(alias='AnswerType')
    name: constr(min_length=2) = Field(alias='Name')
    prompt_mech_chosen: constr(min_length=2) = Field(alias='PromptMechChosen')
    prompt_select_mech: Optional[constr(min_length=2)] = Field(alias='PromptSelectMech')
    mechanism_id: constr(min_length=2) = Field(alias='MechanismId')


class Challenge(ArkModel):
    mechanisms: conlist(Mechanism, min_items=1) = Field(alias='Mechanisms')


class StartAuthResult(ArkModel):
    challenges: Optional[conlist(Challenge, min_items=1)] = Field(alias='Challenges')
    session_id: Optional[constr(min_length=2)] = Field(alias='SessionId')
    idp_redirect_url: Optional[str] = Field(alias='IdpRedirectUrl')
    idp_login_session_id: Optional[str] = Field(alias='IdpLoginSessionId')
    idp_redirect_short_url: Optional[str] = Field(alias='IdpRedirectShortUrl')
    idp_short_url_id: Optional[str] = Field(alias='IdpShortUrlId')
    tenant_id: Optional[str] = Field(alias='TenantId')


class IdpAuthStatusResult(ArkModel):
    state: str = Field(alias='State')
    token_lifetime: Optional[int] = Field(alias='TokenLifetime')
    token: Optional[str] = Field(alias='Token')
    refresh_token: Optional[str] = Field(alias='RefreshToken')


class TenantFqdnResponse(IdentityApiResponse):
    result: PodFqdnResult = Field(alias='Result')


class AdvanceAuthMidResponse(IdentityApiResponse):
    result: AdvanceAuthMidResult = Field(alias='Result')


class AdvanceAuthResponse(IdentityApiResponse):
    result: AdvanceAuthResult = Field(alias='Result')


class StartAuthResponse(IdentityApiResponse):
    result: StartAuthResult = Field(alias='Result')


class GetTenantSuffixResult(IdentityApiResponse):
    result: Optional[Dict] = Field(alias='Result')


class IdpAuthStatusResponse(IdentityApiResponse):
    result: IdpAuthStatusResult = Field(alias='Result')
