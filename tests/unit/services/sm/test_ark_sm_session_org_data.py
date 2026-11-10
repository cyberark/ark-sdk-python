import unittest

from ark_sdk_python.models.services.sm import ArkSMSession

SESSION = {
    'tenantId': 'tenant-id',
    'sessionId': 'session-id',
    'accessMethod': 'Vaulted',
}


class TestArkSMSessionOrgData(unittest.TestCase):
    def test_org_data_is_parsed(self):
        org_data = {'id': 'org-id', 'name': 'org-name'}
        self.assertEqual(ArkSMSession.model_validate({**SESSION, 'orgData': org_data}).org_data, org_data)

    def test_null_org_data_is_none(self):
        self.assertIsNone(ArkSMSession.model_validate({**SESSION, 'orgData': None}).org_data)

    def test_missing_org_data_is_none(self):
        self.assertIsNone(ArkSMSession.model_validate(SESSION).org_data)
