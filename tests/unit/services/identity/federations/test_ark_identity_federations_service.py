import unittest
from http import HTTPStatus
from unittest.mock import MagicMock, patch

from ark_sdk_python.common import get_logger
from ark_sdk_python.models.ark_exceptions import ArkServiceException
from ark_sdk_python.models.services.identity.federations import ArkIdentityFederationsFilter, ArkIdentityGetFederation
from ark_sdk_python.services.identity.federations.ark_identity_federations_service import ArkIdentityFederationsService

SAML = {
    'FederationUuid': 'f1',
    'FederationName': 'Okta',
    'FederationType': 'SAML 2.0',
    'Active': True,
    'Domains': ['acme.com', 'acme.org'],
    'MapUsers': 'Optional',
    'Config': {'IDPSignInUrl': 'https://okta/sso', 'IDPSigningCertificateThumbprint': 'AB12'},
    'Mappings': [{'AttributeValue': 'admins', 'GroupName': 'Admins'}],
    'DeviceTypes': 'Android,iOS',
    'UserAgents': ['Browser'],
}
OIDC = {
    'FederationUuid': 'f2',
    'FederationName': 'Entra',
    'FederationType': 'OIDC',
    'Active': 'false',
    'Domains': 'acme.io, acme.net',
    'MapUsers': 2,
    'OIDCMetaDataUrl': 'https://login.microsoftonline.com/x/.well-known/openid-configuration',
    'OIDCClientId': 'cid',
    'OIDCScopes': ['openid', 'profile'],
    'PKCEEnabled': True,
    'Config': {'LogoutCallBackURI': 'https://logout'},
}
OTHER = {'FederationUuid': 'f3', 'FederationName': 'Other', 'FederationType': 'WSFED'}


class TestFederations(unittest.TestCase):
    def setUp(self):
        service_init_patcher = patch('ark_sdk_python.services.ark_service.ArkService.__init__', return_value=None)
        service_init_patcher.start()
        self.addCleanup(service_init_patcher.stop)
        self.service = ArkIdentityFederationsService.__new__(ArkIdentityFederationsService)
        self.service._logger = get_logger('TestFederations')  # pylint: disable=protected-access
        self.service._url_prefix = 'api/idadmin/'  # pylint: disable=protected-access
        self.client = MagicMock()
        self.service._client = self.client  # pylint: disable=protected-access

    def _respond(self, body, status_code=HTTPStatus.OK):
        response = MagicMock()
        response.status_code = status_code
        response.text = str(body)
        response.json.return_value = body
        return response

    def test_lists_saml_and_oidc_federations(self):
        self.client.post.return_value = self._respond({'success': True, 'Result': [SAML, OIDC, OTHER]})
        federations = self.service.list_federations()
        self.client.post.assert_called_once_with('api/idadmin/Federation/GetFederations', json={})
        self.assertEqual([f.federation_id for f in federations], ['f1', 'f2'])
        saml, oidc = federations
        self.assertEqual(
            (saml.saml_sign_in_url, saml.saml_idp_certificate_thumbprint, saml.saml_sign_algorithm), ('https://okta/sso', 'AB12', 'SHA1')
        )
        self.assertEqual(saml.domains, ['acme.com', 'acme.org'])
        self.assertEqual([(m.attribute_value, m.group_name) for m in saml.group_mappings], [('admins', 'Admins')])
        self.assertEqual((saml.map_users, saml.device_types, saml.user_agents), ('Optional', ['Android', 'iOS'], ['Browser']))
        self.assertFalse(oidc.active)
        self.assertEqual(oidc.domains, ['acme.io', 'acme.net'])
        self.assertEqual(
            (oidc.map_users, oidc.oidc_client_id, oidc.oidc_scopes, oidc.oidc_pkce_enabled),
            ('Required', 'cid', ['openid', 'profile'], True),
        )
        self.assertEqual((oidc.oidc_post_logout_redirect_uri, oidc.user_agents), ('https://logout', ['Any']))

    def test_list_by_filters(self):
        self.client.post.return_value = self._respond({'success': True, 'Result': [SAML, OIDC]})
        self.assertEqual(
            [f.federation_id for f in self.service.list_federations_by(ArkIdentityFederationsFilter(federation_name='ENTRA'))], ['f2']
        )
        self.assertEqual(
            [f.federation_id for f in self.service.list_federations_by(ArkIdentityFederationsFilter(federation_type='SAML 2.0'))], ['f1']
        )

    def test_get_federation(self):
        self.client.post.return_value = self._respond({'success': True, 'Result': OIDC})
        federation = self.service.federation(ArkIdentityGetFederation(federation_id='f2'))
        self.client.post.assert_called_once_with('api/idadmin/Federation/GetFederation', json={'FederationUuid': 'f2'})
        self.assertEqual(federation.federation_name, 'Entra')

    def test_get_missing_federation_reports_not_found(self):
        self.client.post.side_effect = [self._respond({'success': False}), self._respond({'success': True, 'Result': [SAML]})]
        with self.assertRaisesRegex(ArkServiceException, 'was not found'):
            self.service.federation(ArkIdentityGetFederation(federation_id='missing'))

    def test_list_failure_raises(self):
        self.client.post.return_value = self._respond({'success': False})
        with self.assertRaises(ArkServiceException):
            self.service.list_federations()
