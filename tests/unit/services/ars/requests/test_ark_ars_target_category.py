import unittest

from pydantic import ValidationError

from ark_sdk_python.models.common import ArkCategoryType
from ark_sdk_python.models.services.ars.requests import ArkARSListAccessRequestForms
from ark_sdk_python.models.services.ars.requests.ark_target_category import ARS_SUPPORTED_CATEGORIES


class TestArkARSTargetCategory(unittest.TestCase):
    def test_group_is_a_supported_category(self):
        self.assertIn(ArkCategoryType.GROUP, ARS_SUPPORTED_CATEGORIES)
        self.assertEqual(ArkCategoryType.GROUP.value, 'Group')

    def test_group_accepts_name_and_value_and_serializes_as_name(self):
        for value in ('GROUP', 'Group'):
            request = ArkARSListAccessRequestForms(target_category=value)
            self.assertEqual(request.target_category, ArkCategoryType.GROUP)
            self.assertEqual(request.model_dump(mode='json', by_alias=True)['targetCategory'], 'GROUP')

    def test_unsupported_category_is_rejected(self):
        with self.assertRaises(ValidationError):
            ArkARSListAccessRequestForms(target_category='DB')


if __name__ == '__main__':
    unittest.main()
