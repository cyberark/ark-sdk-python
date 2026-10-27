import unittest
from unittest.mock import MagicMock, patch

from ark_sdk_python.models import ArkServiceException
from ark_sdk_python.models.services.pcloud.usermgmt import ArkPCloudVaultUsersFilter
from ark_sdk_python.services.pcloud.usermgmt import ArkPCloudUserMgmtService


def _user(user_id):
    return {
        'id': user_id,
        'username': f'user{user_id}',
        'source': 'CyberArk',
        'userType': 'EPVUser',
        'componentUser': False,
        'vaultAuthorization': [],
    }


def _response(user_ids, total, status=200):
    response = MagicMock()
    response.status_code = status
    response.text = 'body'
    response.json.return_value = {'Users': [_user(i) for i in user_ids], 'Total': total}
    return response


class TestArkPCloudUserMgmtListUsers(unittest.TestCase):
    def setUp(self):
        with patch('ark_sdk_python.services.pcloud.usermgmt.ark_pcloud_usermgmt_service.ArkPCloudBaseService.__init__', return_value=None):
            self.service = ArkPCloudUserMgmtService.__new__(ArkPCloudUserMgmtService)
        self.service._client = MagicMock()
        self.service._logger = MagicMock()
        self.sent = []

    def _serve(self, responses):
        responses = iter(responses)

        def _get(route, **kwargs):
            self.sent.append(dict(kwargs['params']))
            return next(responses)

        self.service._client.get.side_effect = _get

    def test_pages_through_all_users_by_page_offset_and_size(self):
        self._serve([_response([1, 2], 5), _response([3, 4], 5), _response([5], 5)])
        pages = list(self.service.list_vault_users_pages(ArkPCloudVaultUsersFilter(page_size=2)))
        self.assertEqual([[u.id for u in page.items] for page in pages], [[1, 2], [3, 4], [5]])
        self.assertEqual([(p['pageOffset'], p['pageSize']) for p in self.sent], [(0, 2), (2, 2), (4, 2)])

    def test_stops_on_an_empty_page_when_the_total_is_not_reached(self):
        self._serve([_response([1, 2], 99), _response([], 99)])
        self.assertEqual(len(self.service.list_vault_users()), 2)
        self.assertEqual(len(self.sent), 2)

    def test_starts_from_the_given_page_offset(self):
        self._serve([_response([4, 5], 5), _response([], 5)])
        list(self.service.list_vault_users_pages(ArkPCloudVaultUsersFilter(page_size=2, page_offset=3)))
        self.assertEqual(self.sent[0]['pageOffset'], 3)

    def test_a_vault_ignoring_the_paging_does_not_loop_forever(self):
        self._serve([_response([1, 2, 3], 3)] * 5)
        self.assertEqual([u.id for u in self.service.list_vault_users()], [1, 2, 3])
        self.assertLessEqual(len(self.sent), 2)

    def test_filters_are_sent_as_the_rest_filter(self):
        self._serve([_response([], 0)])
        filters = ArkPCloudVaultUsersFilter(user_type='EPVUser', component_user=False, user_name='jdoe', search='jd', sort='username asc')
        self.service.list_vault_users_by(filters)
        params = self.sent[0]
        self.assertEqual(params['filter'], 'userType eq EPVUser AND componentUser eq false AND userName eq jdoe')
        self.assertEqual((params['search'], params['sort'], params['ExtendedDetails']), ('jd', 'username asc', True))
        for legacy in ('userType', 'componentUser', 'userName'):
            self.assertNotIn(legacy, params)

    def test_no_filter_param_without_filters_and_extended_details_can_be_off(self):
        self._serve([_response([], 0)])
        self.service.list_vault_users_by(ArkPCloudVaultUsersFilter(extended_details=False))
        self.assertNotIn('filter', self.sent[0])
        self.assertFalse(self.sent[0]['ExtendedDetails'])

    def test_failed_call_raises_with_the_status(self):
        self._serve([_response([], 0, status=504)])
        with self.assertRaises(ArkServiceException) as ctx:
            self.service.list_vault_users()
        self.assertIn('[504]', str(ctx.exception.error))


if __name__ == '__main__':
    unittest.main()
