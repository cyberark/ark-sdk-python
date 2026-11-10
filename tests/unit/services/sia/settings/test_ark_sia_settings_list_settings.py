import unittest
from http import HTTPStatus
from unittest.mock import MagicMock, patch

from ark_sdk_python.common import get_logger
from ark_sdk_python.models.services.sia.settings import ArkSIASettingsListSettings
from ark_sdk_python.services.sia.settings.ark_sia_settings_service import ArkSIASettingsService


class TestListSettings(unittest.TestCase):
    def setUp(self):
        client_patcher = patch('ark_sdk_python.services.sia.settings.ark_sia_settings_service.ArkISPServiceClient')
        service_init_patcher = patch('ark_sdk_python.services.ark_service.ArkService.__init__', return_value=None)
        mock_client_class = client_patcher.start()
        service_init_patcher.start()
        self.addCleanup(client_patcher.stop)
        self.addCleanup(service_init_patcher.stop)

        self.service = ArkSIASettingsService(MagicMock())
        self.service._logger = get_logger('TestListSettings')  # pylint: disable=protected-access
        self.mock_client = mock_client_class.from_isp_auth.return_value
        response = MagicMock()
        response.status_code = HTTPStatus.OK
        response.text = '{}'
        self.mock_client.get.return_value = response

    def test_default_list_reads_the_tenant_settings(self):
        # The service answers the environment defaults whenever `default` is present, even `default=False`
        self.service.list_settings(ArkSIASettingsListSettings())
        self.assertIsNone(self.mock_client.get.call_args.kwargs['params'])

    def test_default_false_reads_the_tenant_settings(self):
        self.service.list_settings(ArkSIASettingsListSettings(default=False))
        self.assertIsNone(self.mock_client.get.call_args.kwargs['params'])

    def test_default_true_reads_the_environment_defaults(self):
        self.service.list_settings(ArkSIASettingsListSettings(default=True))
        self.assertEqual(self.mock_client.get.call_args.kwargs['params'], {'default': 'true'})
