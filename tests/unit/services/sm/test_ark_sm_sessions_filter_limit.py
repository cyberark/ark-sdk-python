import unittest
from unittest.mock import MagicMock, patch

from ark_sdk_python.models.services.sm import ArkSMSessionsFilter
from ark_sdk_python.services.sm.ark_sm_service import ArkSMService


def _response(sessions, returned_count):
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {'sessions': sessions, 'filteredCount': 3, 'returnedCount': returned_count}
    return response


def _session(session_id):
    return {'tenantId': 't', 'sessionId': session_id}


class TestArkSMSessionsFilterLimit(unittest.TestCase):
    def setUp(self):
        with patch('ark_sdk_python.services.sm.ark_sm_service.ArkService.__init__', return_value=None):
            self.service = ArkSMService.__new__(ArkSMService)
        self.client = MagicMock()
        self.service._ArkSMService__client = self.client  # pylint: disable=protected-access
        self.service._logger = MagicMock()  # pylint: disable=protected-access

    def test_limit_is_optional(self):
        self.assertIsNone(ArkSMSessionsFilter(search='x').limit)

    def test_limit_must_be_positive(self):
        with self.assertRaises(ValueError):
            ArkSMSessionsFilter(search='x', limit=0)

    def test_limit_is_sent_on_every_page_and_paging_follows_the_returned_count(self):
        responses = iter([_response([_session('1'), _session('2')], 2), _response([_session('3')], 1), _response([], 0)])
        sent = []

        def _get(_route, **kwargs):
            sent.append(dict(kwargs['params']))  # the service reuses and mutates one params dict, so copy it per call
            return next(responses)

        self.client.get.side_effect = _get
        pages = list(self.service.list_sessions_by(ArkSMSessionsFilter(search='x', limit=500)))
        self.assertEqual([len(page.items) for page in pages], [2, 1])
        self.assertEqual([p.get('offset') for p in sent], [None, 2, 3])
        self.assertTrue(all(p['limit'] == 500 and p['search'] == 'x' for p in sent))

    def test_no_limit_param_when_not_given(self):
        self.client.get.side_effect = [_response([], 0)]
        list(self.service.list_sessions_by(ArkSMSessionsFilter(search='x')))
        self.assertNotIn('limit', self.client.get.call_args.kwargs['params'])


if __name__ == '__main__':
    unittest.main()
