import json
import unittest
from http import HTTPStatus
from unittest.mock import MagicMock, patch

from ark_sdk_python.common import get_logger
from ark_sdk_python.models.common.identity import DirectoryService
from ark_sdk_python.models.services.identity.directories import ArkIdentityListDirectories
from ark_sdk_python.services.identity.directories.ark_identity_directories_service import ArkIdentityDirectoriesService

RESPONSE = {
    'success': True,
    'Result': {
        'Results': [
            {'Row': {'Service': 'CDS', 'directoryServiceUuid': 'd1', 'Config': 'Cloud Directory', 'DisplayNameShort': 'CDS'}},
            {'Row': {'Service': 'AdProxy', 'directoryServiceUuid': 'd2', 'Config': 'corp.local'}},
            {'Row': {'Service': 'FDS', 'directoryServiceUuid': 'd3', 'DisplayNameShort': 'Federated'}},
        ]
    },
}


class TestListDirectories(unittest.TestCase):
    def setUp(self):
        service_init_patcher = patch('ark_sdk_python.services.ark_service.ArkService.__init__', return_value=None)
        service_init_patcher.start()
        self.addCleanup(service_init_patcher.stop)
        self.service = ArkIdentityDirectoriesService.__new__(ArkIdentityDirectoriesService)
        self.service._logger = get_logger('TestListDirectories')  # pylint: disable=protected-access
        self.service._url_prefix = 'api/idadmin/'  # pylint: disable=protected-access
        self.service._client = MagicMock()  # pylint: disable=protected-access
        response = MagicMock()
        response.status_code = HTTPStatus.OK
        response.text = json.dumps(RESPONSE)
        self.service._client.get.return_value = response  # pylint: disable=protected-access

    def test_lists_every_directory_with_its_names(self):
        directories = self.service.list_directories(ArkIdentityListDirectories())
        self.assertEqual(
            [(d.directory, d.directory_service_uuid, d.config, d.display_name) for d in directories],
            [
                (DirectoryService.Identity, 'd1', 'Cloud Directory', 'CDS'),
                (DirectoryService.AD, 'd2', 'corp.local', None),
                (DirectoryService.FDS, 'd3', None, 'Federated'),
            ],
        )

    def test_filters_by_type(self):
        directories = self.service.list_directories(ArkIdentityListDirectories(directories=[DirectoryService.AD]))
        self.assertEqual([d.directory_service_uuid for d in directories], ['d2'])
