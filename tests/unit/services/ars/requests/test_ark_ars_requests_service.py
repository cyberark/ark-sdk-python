import unittest
from unittest.mock import MagicMock, patch

from ark_sdk_python.models.services.ars.common import ArkARSSortDirection, ArkARSSortQuery
from ark_sdk_python.services.ars.requests.ark_ars_requests_service import ArkARSRequestsService


class TestArkARSRequestsService(unittest.TestCase):

    def setUp(self):
        self.mock_isp_auth = MagicMock()
        self.patches = [
            patch('ark_sdk_python.services.ars.requests.ark_ars_requests_service.ArkISPServiceClient'),
            patch('ark_sdk_python.services.ars.requests.ark_ars_requests_service.os.getenv', return_value='prod'),
            patch('ark_sdk_python.services.ars.requests.ark_ars_requests_service.ArkService.__init__', return_value=None),
        ]
        for patcher in self.patches:
            patcher.start()

        self.service = ArkARSRequestsService(self.mock_isp_auth)

    def tearDown(self):
        for patcher in self.patches:
            patcher.stop()

    def test_parse_sort_parameter_single_query_with_direction(self):
        sort_query = ArkARSSortQuery(field="created_at", direction=ArkARSSortDirection.DESC)
        result = self.service._parse_sort_parameter(sort_query)  # pylint: disable=protected-access
        self.assertEqual(result, "created_at desc")

    def test_parse_sort_parameter_single_query_without_direction(self):
        sort_query = ArkARSSortQuery(field="name")
        result = self.service._parse_sort_parameter(sort_query)  # pylint: disable=protected-access
        self.assertEqual(result, "name")

    def test_parse_sort_parameter_multiple_queries(self):
        sort_queries = [
            ArkARSSortQuery(field="created_at", direction=ArkARSSortDirection.DESC),
            ArkARSSortQuery(field="name", direction=ArkARSSortDirection.ASC),
        ]
        result = self.service._parse_sort_parameter(sort_queries)  # pylint: disable=protected-access
        self.assertEqual(result, "created_at desc,name asc")

    def test_parse_sort_parameter_mixed_queries(self):
        sort_queries = [ArkARSSortQuery(field="created_at", direction=ArkARSSortDirection.DESC), ArkARSSortQuery(field="name")]
        result = self.service._parse_sort_parameter(sort_queries)  # pylint: disable=protected-access
        self.assertEqual(result, "created_at desc,name")

    def test_parse_sort_parameter_empty_list(self):
        sort_queries = []
        result = self.service._parse_sort_parameter(sort_queries)  # pylint: disable=protected-access
        self.assertEqual(result, "")

    def test_parse_sort_parameter_missing_field(self):
        sort_queries = [
            ArkARSSortQuery(direction=ArkARSSortDirection.DESC),
            ArkARSSortQuery(field="name", direction=ArkARSSortDirection.ASC),
        ]
        result = self.service._parse_sort_parameter(sort_queries)  # pylint: disable=protected-access
        self.assertEqual(result, "name asc")

    def test_parse_sort_parameter_all_missing_fields(self):
        sort_queries = [ArkARSSortQuery(direction=ArkARSSortDirection.DESC), ArkARSSortQuery(direction=ArkARSSortDirection.ASC)]
        result = self.service._parse_sort_parameter(sort_queries)  # pylint: disable=protected-access
        self.assertEqual(result, "")


if __name__ == '__main__':
    unittest.main()
