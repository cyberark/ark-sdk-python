import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from requests.auth import HTTPBasicAuth

from ark_sdk_python.auth import ArkISPAuth
from ark_sdk_python.models.auth import ArkAuthMethod, ArkSecret, ArkToken
from tests.unit.helpers import (
    ADVANCE_AUTH_SUCCESS_RESPONSE,
    OAUTH_AUTHORIZE_SUCCESS_RESPONSE,
    OAUTH_TOKEN_SUCCESS_RESPONSE,
    START_AUTH_SUCCESS_RESPONSE,
    generate_auth_profile_for,
    generate_profile_for,
)


class TestArkISPAuth:
    @pytest.fixture(scope='module', autouse=True)
    def env_config(self):
        os.environ.update({'DEPLOY_ENV': 'prod'})

    @pytest.mark.parametrize('auth_method', [ArkAuthMethod.Default, ArkAuthMethod.Identity])
    @pytest.mark.parametrize('from_profile', ['Yes', 'No', 'Both'])
    def test_identity_auth_method(self, mocker: MockerFixture, auth_method: ArkAuthMethod, from_profile: str):
        tenant_fqdn_mock = mocker.patch(
            'ark_sdk_python.auth.identity.ark_identity_fqdn_resolver.ArkIdentityFQDNResolver.resolve_tenant_fqdn_from_tenant_suffix'
        )
        tenant_fqdn_mock.return_value = 'https://url.com'
        session_mock = mocker.patch('ark_sdk_python.auth.identity.ark_identity.Session')
        session_mock.return_value.post = MagicMock()
        session_mock.return_value.post.side_effect = [START_AUTH_SUCCESS_RESPONSE, ADVANCE_AUTH_SUCCESS_RESPONSE]
        session_mock.return_value.cookies = {}
        auth = ArkISPAuth(cache_authentication=False)
        token = auth.authenticate(
            generate_profile_for('isp', auth_method) if from_profile in ['Yes', 'Both'] else None,
            generate_auth_profile_for(auth_method) if from_profile in ['No', 'Both'] else None,
            ArkSecret(secret='secret'),
        )
        assert token
        assert token.username == 'user@user.com'
        assert token.endpoint == 'https://url.com'
        assert token.token.get_secret_value() == 'token'
        assert 'cookies' in token.metadata
        tenant_fqdn_mock.assert_called_once()
        session_mock.return_value.post.assert_any_call(
            url='https://url.com/Security/StartAuthentication',
            json={'User': 'user@user.com', 'Version': '1.0', 'PlatformTokenResponse': True, 'MfaRequestor': 'DeviceAgent'},
        )
        session_mock.return_value.post.assert_any_call(
            url='https://url.com/Security/AdvanceAuthentication',
            json={'SessionId': '1234', 'MechanismId': '1234', 'Action': 'Answer', 'Answer': 'secret'},
        )

    @pytest.mark.parametrize('from_profile', ['Yes', 'No', 'Both'])
    def test_identity_service_user_auth_method(self, mocker: MockerFixture, from_profile: str):
        tenant_fqdn_mock = mocker.patch(
            'ark_sdk_python.auth.identity.ark_identity_fqdn_resolver.ArkIdentityFQDNResolver.resolve_tenant_fqdn_from_tenant_suffix'
        )
        tenant_fqdn_mock.return_value = 'https://url.com'
        session_mock = mocker.patch('ark_sdk_python.auth.identity.ark_identity_service_user.Session')
        session_mock.return_value.post = MagicMock()
        session_mock.return_value.post.side_effect = [OAUTH_TOKEN_SUCCESS_RESPONSE]
        session_mock.return_value.get = MagicMock()
        session_mock.return_value.get.side_effect = [OAUTH_AUTHORIZE_SUCCESS_RESPONSE]
        session_mock.return_value.cookies = {}
        auth = ArkISPAuth(cache_authentication=False)
        token = auth.authenticate(
            generate_profile_for('isp', ArkAuthMethod.IdentityServiceUser) if from_profile in ['Yes', 'Both'] else None,
            generate_auth_profile_for(ArkAuthMethod.IdentityServiceUser) if from_profile in ['No', 'Both'] else None,
            ArkSecret(secret='token'),
        )
        assert token
        assert token.username == 'user@user.com'
        assert token.endpoint == 'https://url.com'
        assert token.token.get_secret_value() == 'id_token'
        assert 'cookies' in token.metadata
        tenant_fqdn_mock.assert_called_once()
        session_mock.return_value.post.assert_any_call(
            url='https://url.com/Oauth2/Token/__identity_cybr_user_oidc',
            auth=HTTPBasicAuth('user@user.com', 'token'),
            verify=True,
            data={'grant_type': 'client_credentials', 'scope': 'api'},
        )
        session_mock.return_value.get.assert_any_call(
            url='https://url.com/OAuth2/Authorize/__identity_cybr_user_oidc',
            headers={'Authorization': 'Bearer access_token'},
            params={
                'client_id': '__identity_cybr_user_oidc',
                'response_type': 'id_token',
                'scope': 'openid profile api',
                'redirect_uri': 'https://cyberark.cloud/redirect',
            },
            allow_redirects=False,
        )

    def test_identity_auth_method_caching(self, mocker: MockerFixture):
        pickle_dumps_mock = mocker.patch('dill.dumps')
        pickle_dumps_mock.return_value = 'abcd'.encode('utf-8')
        tenant_fqdn_mock = mocker.patch(
            'ark_sdk_python.auth.identity.ark_identity_fqdn_resolver.ArkIdentityFQDNResolver.resolve_tenant_fqdn_from_tenant_suffix'
        )
        tenant_fqdn_mock.return_value = 'https://url.com'
        keyring_load_mock = mocker.patch('ark_sdk_python.common.ark_keyring.ArkKeyring.load_token')
        keyring_save_mock = mocker.patch('ark_sdk_python.common.ark_keyring.ArkKeyring.save_token')
        keyring_load_mock.side_effect = [
            None,
            None,
            None,
            ArkToken(token='cached_token', auth_method=ArkAuthMethod.Identity, expires_in=datetime.now() + timedelta(minutes=5)),
        ]
        session_mock = mocker.patch('ark_sdk_python.auth.identity.ark_identity.Session')
        session_mock.return_value.post = MagicMock()
        session_mock.return_value.post.side_effect = [START_AUTH_SUCCESS_RESPONSE, ADVANCE_AUTH_SUCCESS_RESPONSE]
        session_mock.return_value.cookies = {}
        auth = ArkISPAuth(cache_authentication=True)
        token = auth.authenticate(generate_profile_for('isp', ArkAuthMethod.Identity), None, ArkSecret(secret='secret'))
        assert token
        assert token.username == 'user@user.com'
        assert token.endpoint == 'https://url.com'
        assert token.token.get_secret_value() == 'token'
        assert 'cookies' in token.metadata
        tenant_fqdn_mock.assert_called_once()
        keyring_load_mock.assert_called()
        keyring_save_mock.assert_called()
        pickle_dumps_mock.assert_called()
        session_mock.return_value.post.assert_any_call(
            url='https://url.com/Security/StartAuthentication',
            json={'User': 'user@user.com', 'Version': '1.0', 'PlatformTokenResponse': True, 'MfaRequestor': 'DeviceAgent'},
        )
        session_mock.return_value.post.assert_any_call(
            url='https://url.com/Security/AdvanceAuthentication',
            json={'SessionId': '1234', 'MechanismId': '1234', 'Action': 'Answer', 'Answer': 'secret'},
        )
        token = auth.authenticate(generate_profile_for('isp', ArkAuthMethod.Identity), None, ArkSecret(secret='secret'))
        assert token
        assert token.token.get_secret_value() == 'cached_token'
