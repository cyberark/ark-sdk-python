import json
from collections import namedtuple
from http import HTTPStatus

from ark_sdk_python.models.common.identity import (
    AdvanceAuthResponse,
    AdvanceAuthResult,
    Challenge,
    Mechanism,
    StartAuthResponse,
    StartAuthResult,
)

MockResponse = namedtuple('MockResponse', ['status_code', 'text', 'headers', 'cookies'], defaults=(HTTPStatus.OK, '', {}, {}))

START_AUTH_SUCCESS_RESPONSE = MockResponse(
    status_code=HTTPStatus.OK,
    text=StartAuthResponse(
        success=True,
        result=StartAuthResult(
            session_id='1234',
            challenges=[
                Challenge(
                    mechanisms=[
                        Mechanism(
                            name='UP', answer_type='Text', prompt_mech_chosen='Gosh', prompt_select_mech='Shoosh', mechanism_id='1234'
                        )
                    ]
                )
            ],
        ),
    ).model_dump_json(),
)

ADVANCE_AUTH_SUCCESS_RESPONSE = MockResponse(
    status_code=HTTPStatus.OK,
    text=AdvanceAuthResponse(
        success=True,
        result=AdvanceAuthResult(
            display_name='abcd',
            auth='efg',
            summary='LoginSuccess',
            token='token',
            refresh_token='token',
            token_lifetime=123,
            customer_id='123',
            user_id='userid',
            pod_fqdn='pod',
        ),
    ).model_dump_json(),
)

OAUTH_TOKEN_SUCCESS_RESPONSE = MockResponse(status_code=HTTPStatus.OK, text=json.dumps({'access_token': 'access_token'}))

OAUTH_AUTHORIZE_SUCCESS_RESPONSE = MockResponse(
    status_code=HTTPStatus.FOUND, headers={'Location': 'https://location.com/#id_token=id_token'}
)

CYBR_TOKEN_SUCCESS_RESPONSE = MockResponse(
    status_code=HTTPStatus.OK,
    text=json.dumps({'success': True, 'Result': {'Token': 'token', 'Hostname': 'https://url.com', 'ExpiresIn': 900}}),
)

GET_APPS_RESPONSE = MockResponse(
    status_code=HTTPStatus.OK,
    text=json.dumps(
        {'success': True, 'Result': {'Apps': [{'Name': 'application', 'Url': 'https://url.cyberark.cloud', '_RowKey': 'app_key'}]}}
    ),
)

SAML_REDIRECT_RESPONSE = MockResponse(
    status_code=HTTPStatus.OK,
    text='''
    <form method="post" action="https://redirect.cyberark.cloud" name="myform">
        <input type="hidden" name="SAMLResponse" value="response" />
        <input type="hidden" name="RelayState" value="url" />
        <input type="submit" value="Submit" />
    </form>
    ''',
)

SAML_RESP_LOC_RESPONSE = MockResponse(status_code=HTTPStatus.FOUND, headers={'Location': 'https://location.cyberark.cloud'})

SAML_RESP_NON_LOC_RESPONSE = MockResponse(status_code=HTTPStatus.OK, text=json.dumps({'id_token': 'id_token', 'expires_in': 3600}))

SAML_RESP_SUCCESS_RESPONSE = MockResponse(status_code=HTTPStatus.OK)

SAML_SUCCESS_RESPONSE = MockResponse(status_code=HTTPStatus.OK, cookies={'idToken': 'id_token', 'refreshToken': 'refresh_token'})

SAML_SSO_COMPLETE_SUCESS_RESPONSE = MockResponse(status_code=HTTPStatus.OK)

HANDLE_APP_KEY_RESPONSE = MockResponse(
    status_code=HTTPStatus.OK,
    text='''
    <form method="post" action="https://redirect.cyberark.cloud" name="myform">
        <input type="hidden" name="SAMLResponse" value="response" />
        <input type="hidden" name="RelayState" value="url" />
        <input type="submit" value="Submit" />
    </form>
    ''',
)
