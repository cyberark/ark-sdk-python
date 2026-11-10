import unittest

import pytest
from pydantic import ValidationError

from ark_sdk_python.models.services.sia.sso import ArkSIASSOGetShortLivedRDPFile


@pytest.mark.parametrize(
    'vaulted_account_id',
    ['abc', '10', '10_', '_10', '-1_5', '1.0_5', '10_10_10', ' 10_10', '10_10\n'],
    ids=[
        'NotNumeric',
        'MissingSeparator',
        'MissingAccountId',
        'MissingSafeId',
        'Negative',
        'Decimal',
        'TooManyParts',
        'LeadingSpace',
        'TrailingNewline',
    ],
)
def test_error_malformed_vaulted_account_id(vaulted_account_id):
    """Test that a vaulted account id which is not of the <safe id>_<account id> format raises ValidationError."""
    with pytest.raises(ValidationError, match='<safe id>_<account id>'):
        ArkSIASSOGetShortLivedRDPFile(
            folder='/tmp',
            target_address='mymachine.mydomain.com',
            target_user='myuser',
            vaulted_account_id=vaulted_account_id,
        )


class TestGetShortLivedRDPFileValidation(unittest.TestCase):
    def test_valid_vaulted_account_id(self):
        """Test that a vaulted account id given along with a target user is accepted."""
        rdp_file = ArkSIASSOGetShortLivedRDPFile(
            folder='/tmp',
            target_address='mymachine.mydomain.com',
            target_user='myuser',
            vaulted_account_id='10_10',
        )

        self.assertEqual(rdp_file.vaulted_account_id, '10_10')

    def test_valid_zeroed_vaulted_account_id(self):
        """Test that 0_0 is accepted, as the validation matches the proxy regex rather than requiring positive ids."""
        rdp_file = ArkSIASSOGetShortLivedRDPFile(
            folder='/tmp',
            target_address='mymachine.mydomain.com',
            target_user='myuser',
            vaulted_account_id='0_0',
        )

        self.assertEqual(rdp_file.vaulted_account_id, '0_0')

    def test_error_vaulted_account_id_without_target_user(self):
        """Test that a vaulted account id without a target user raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            ArkSIASSOGetShortLivedRDPFile(
                folder='/tmp',
                target_address='mymachine.mydomain.com',
                vaulted_account_id='10_10',
            )

        self.assertIn('requires a target user', str(context.exception))

    def test_valid_without_vaulted_account_id(self):
        """Test that omitting the vaulted account id keeps working for existing callers."""
        rdp_file = ArkSIASSOGetShortLivedRDPFile(
            folder='/tmp',
            target_address='mymachine.mydomain.com',
            target_user='myuser',
        )

        self.assertIsNone(rdp_file.vaulted_account_id)

    def test_valid_without_vaulted_account_id_and_explicit_none_target_user(self):
        """Test that an explicitly None target user is fine as long as no vaulted account id is given."""
        rdp_file = ArkSIASSOGetShortLivedRDPFile(
            folder='/tmp',
            target_address='mymachine.mydomain.com',
            target_user=None,
            vaulted_account_id=None,
        )

        self.assertIsNone(rdp_file.vaulted_account_id)
