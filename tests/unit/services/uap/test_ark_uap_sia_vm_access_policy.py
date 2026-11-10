import unittest

from ark_sdk_python.models.common.ark_category_type import ArkCategoryType
from ark_sdk_python.models.common.ark_workspace_type import ArkWorkspaceType
from ark_sdk_python.models.services.uap.common import (
    ArkUAPAccessApproval,
    ArkUAPConditions,
    ArkUAPMetadata,
    ArkUAPPolicyEntitlement,
    ArkUAPPolicyStatus,
    ArkUAPPrincipal,
    ArkUAPPrincipalType,
    ArkUAPStatusType,
)
from ark_sdk_python.models.services.uap.sia.common.ark_uap_sia_common_conditions import ArkUAPSIACommonConditions
from ark_sdk_python.models.services.uap.sia.vm import ArkUAPSIAVMAccessPolicy, ArkUAPSIAVMPlatformTargets, ArkUAPSSIAVMBehavior
from ark_sdk_python.models.services.uap.sia.vm.ark_uap_sia_vm_behavior import ArkUAPSSIAVMSSHProfile
from ark_sdk_python.models.services.uap.sia.vm.ark_uap_sia_vm_conditions import ArkUAPSIAVMConditions
from ark_sdk_python.models.services.uap.sia.vm.ark_uap_sia_vm_targets import ArkUAPSIAVMAWSResource


class TestArkUAPSIAVMAccessPolicy(unittest.TestCase):

    @staticmethod
    def _create_policy(with_approval: bool = True) -> ArkUAPSIAVMAccessPolicy:
        access_approval = None
        if with_approval:
            access_approval = ArkUAPAccessApproval(
                required=True,
                approvers=[
                    ArkUAPPrincipal(
                        id='approver-1',
                        name='approver.one',
                        source_directory_name='example',
                        source_directory_id='example-id',
                        type=ArkUAPPrincipalType.USER,
                    )
                ],
            )

        return ArkUAPSIAVMAccessPolicy(
            metadata=ArkUAPMetadata(
                name='vm policy',
                status=ArkUAPPolicyStatus(status=ArkUAPStatusType.ACTIVE),
                policy_entitlement=ArkUAPPolicyEntitlement(
                    target_category=ArkCategoryType.VM,
                    location_type=ArkWorkspaceType.AWS,
                ),
            ),
            conditions=ArkUAPSIAVMConditions(access_approval=access_approval),
            targets=ArkUAPSIAVMPlatformTargets(
                aws_resource=ArkUAPSIAVMAWSResource(
                    regions=['us-east-1'],
                    tags=[],
                    vpc_ids=['vpc-12345678'],
                    account_ids=['123456789012'],
                )
            ),
            behavior=ArkUAPSSIAVMBehavior(ssh_profile=ArkUAPSSIAVMSSHProfile(username='root')),
        )

    def test_serialize_model_includes_access_approval(self):
        policy = self._create_policy(with_approval=True)

        serialized = policy.serialize_model(by_alias=True, exclude_none=True)

        self.assertIn('conditions', serialized)
        self.assertIn('accessApproval', serialized['conditions'])
        self.assertTrue(serialized['conditions']['accessApproval']['required'])
        self.assertEqual(serialized['conditions']['accessApproval']['approvers'][0]['id'], 'approver-1')

    def test_serialize_model_omits_access_approval_when_not_set(self):
        policy = self._create_policy(with_approval=False)

        serialized = policy.serialize_model(by_alias=True, exclude_none=True)

        self.assertIn('conditions', serialized)
        self.assertNotIn('accessApproval', serialized['conditions'])

    def test_conditions_model_dump_omits_access_approval_when_not_set(self):
        # Serializer on ArkUAPConditions; SIA VM conditions inherit it.
        self.assertNotIn('accessApproval', ArkUAPConditions().model_dump(by_alias=True))
        self.assertNotIn('accessApproval', ArkUAPSIACommonConditions().model_dump(by_alias=True))

    def test_deserialize_model_preserves_access_approval(self):
        serialized = self._create_policy(with_approval=True).serialize_model(by_alias=True, exclude_none=True)

        deserialized = ArkUAPSIAVMAccessPolicy.deserialize_model(serialized)

        self.assertIsNotNone(deserialized.conditions.access_approval)
        self.assertTrue(deserialized.conditions.access_approval.required)
        self.assertEqual(deserialized.conditions.access_approval.approvers[0].id, 'approver-1')

    # --- override and recording fields ---

    def _create_policy_with_vm_conditions(self, conditions: ArkUAPSIAVMConditions) -> ArkUAPSIAVMAccessPolicy:
        policy = self._create_policy(with_approval=False)
        policy.conditions = conditions
        return policy

    def test_override_fields_omitted_when_none(self):
        """None values must be excluded from the serialized payload (omitempty)."""
        policy = self._create_policy_with_vm_conditions(ArkUAPSIAVMConditions())

        serialized = policy.serialize_model(by_alias=True, exclude_none=True)
        conditions = serialized['conditions']

        self.assertNotIn('overrideIdleTime', conditions)
        self.assertNotIn('overrideMaxSessionDuration', conditions)
        self.assertNotIn('recording', conditions)
        self.assertNotIn('overrideRecording', conditions)

    def test_override_fields_present_when_true(self):
        """Explicit True must be serialized on the wire."""
        policy = self._create_policy_with_vm_conditions(
            ArkUAPSIAVMConditions(
                override_idle_time=True,
                override_max_session_duration=True,
                recording=True,
                override_recording=True,
            )
        )

        serialized = policy.serialize_model(by_alias=True, exclude_none=True)
        conditions = serialized['conditions']

        self.assertEqual(conditions['overrideIdleTime'], True)
        self.assertEqual(conditions['overrideMaxSessionDuration'], True)
        self.assertEqual(conditions['recording'], True)
        self.assertEqual(conditions['overrideRecording'], True)

    def test_override_fields_present_when_false(self):
        """Explicit False must be serialized — False is not the same as None."""
        policy = self._create_policy_with_vm_conditions(
            ArkUAPSIAVMConditions(
                override_idle_time=False,
                override_max_session_duration=False,
                recording=False,
                override_recording=False,
            )
        )

        serialized = policy.serialize_model(by_alias=True, exclude_none=True)
        conditions = serialized['conditions']

        self.assertEqual(conditions['overrideIdleTime'], False)
        self.assertEqual(conditions['overrideMaxSessionDuration'], False)
        self.assertEqual(conditions['recording'], False)
        self.assertEqual(conditions['overrideRecording'], False)

    def test_recording_fields_are_vm_only(self):
        """recording and override_recording must not exist on the shared common conditions model."""
        common = ArkUAPSIACommonConditions()

        self.assertFalse(hasattr(common, 'recording'))
        self.assertFalse(hasattr(common, 'override_recording'))
