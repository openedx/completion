"""
Tests of completion xblock runtime services
"""

from unittest.mock import Mock

import ddt
from django.test import TestCase
from django.test.utils import override_settings
from opaque_keys.edx.keys import CourseKey, UsageKey
from xblock.completable import XBlockCompletionMode
from xblock.core import XBlock
from xblock.fields import ScopeIds

from ..models import BlockCompletion
from ..services import CompletionService
from ..test_utils import CompletionSetUpMixin, UserFactory


@ddt.ddt
class CompletionServiceTestCase(CompletionSetUpMixin, TestCase):
    """
    Test the data returned by the CompletionService.
    """
    COMPLETION_SWITCH_ENABLED = True

    def setUp(self):
        super(CompletionServiceTestCase, self).setUp()
        self.user = UserFactory.create()
        self.other_user = UserFactory.create()
        self.course_key = CourseKey.from_string("edX/MOOC101/2049_T2")
        self.other_course_key = CourseKey.from_string("course-v1:ReedX+Hum110+1904")
        self.block_keys = [
            UsageKey.from_string(
                "i4x://edX/MOOC101/video/{}".format(number)
            ).replace(course_key=self.course_key) for number in range(5)
        ]
        self.other_course_block_keys = [
            self.other_course_key.make_usage_key('video', 'id')
        ]

        self.completion_service = CompletionService(self.user, self.course_key)

        # Proper completions for the given runtime
        for idx, block_key in enumerate(self.block_keys[0:3]):
            BlockCompletion.objects.submit_completion(
                user=self.user,
                block_key=block_key,
                completion=1.0 - (0.2 * idx),
            )

        # Wrong user
        for idx, block_key in enumerate(self.block_keys[2:]):
            BlockCompletion.objects.submit_completion(
                user=self.other_user,
                block_key=block_key,
                completion=0.9 - (0.2 * idx),
            )

        # Wrong course
        BlockCompletion.objects.submit_completion(
            user=self.user,
            block_key=self.other_course_block_keys[0],
            completion=0.75,
        )

    def test_get_completion(self):
        actual_completions = self.completion_service.get_completions(self.block_keys)
        expected_completions = dict(zip(self.block_keys, [1.0, 0.8, 0.6, 0.0, 0.0]))
        self.assertEqual(expected_completions, actual_completions)

    def test_submit_completion(self):
        completable_block = XBlock(Mock(), scope_ids=Mock(spec=ScopeIds))
        completable_block.location = UsageKey.from_string("i4x://edX/100/a/1").replace(course_key=self.course_key)
        service = CompletionService(self.user, self.course_key)
        service.submit_completion(completable_block.location, 0.75)
        self.assertEqual(BlockCompletion.objects.get(block_key=completable_block.location).completion, 0.75)

    def test_submit_group_completion(self):
        third_user = UserFactory.create()
        completable_block = XBlock(Mock(), scope_ids=Mock(spec=ScopeIds))
        completable_block.location = UsageKey.from_string("i4x://edX/100/a/1").replace(course_key=self.course_key)
        service = CompletionService(self.user, self.course_key)
        service.submit_group_completion(
            block_key=completable_block.location,
            completion=0.25,
            users=[self.other_user, third_user],
        )
        completions = list(BlockCompletion.objects.filter(block_key=completable_block.location))
        self.assertEqual(len(completions), 2)
        self.assertTrue(all(bc.completion == 0.25 for bc in completions))
        self.assertEqual({bc.user for bc in completions}, {self.other_user, third_user})

    def test_submit_group_completion_by_user_ids(self):
        third_user = UserFactory.create()
        completable_block = XBlock(Mock(), scope_ids=Mock(spec=ScopeIds))
        completable_block.location = UsageKey.from_string("i4x://edX/100/a/1").replace(course_key=self.course_key)
        service = CompletionService(self.user, self.course_key)
        service.submit_group_completion(
            block_key=completable_block.location,
            completion=0.25,
            user_ids=[self.other_user.id, third_user.id],
        )
        completions = list(BlockCompletion.objects.filter(block_key=completable_block.location))
        self.assertEqual(len(completions), 2)
        self.assertTrue(all(bc.completion == 0.25 for bc in completions))
        self.assertEqual({bc.user for bc in completions}, {self.other_user, third_user})

    def test_submit_group_completion_by_mixed_users_and_user_ids(self):
        third_user = UserFactory.create()
        completable_block = XBlock(Mock(), scope_ids=Mock(spec=ScopeIds))
        completable_block.location = UsageKey.from_string("i4x://edX/100/a/1").replace(course_key=self.course_key)
        service = CompletionService(self.user, self.course_key)
        service.submit_group_completion(
            block_key=completable_block.location,
            completion=0.25,
            users=[self.other_user],
            user_ids=[third_user.id],
        )
        completions = list(BlockCompletion.objects.filter(block_key=completable_block.location))
        self.assertEqual(len(completions), 2)
        self.assertTrue(all(bc.completion == 0.25 for bc in completions))
        self.assertEqual({bc.user for bc in completions}, {self.other_user, third_user})

    def test_get_completions_block_keys_missing_run(self):
        candidates = [
            UsageKey.from_string("i4x://edX/MOOC101/video/{}".format(number)) for number in range(5)
        ]
        actual_completions = self.completion_service.get_completions(candidates)
        expected_block_keys = [key.replace(course_key=self.course_key) for key in candidates]
        expected_completions = dict(zip(expected_block_keys, [1.0, 0.8, 0.6, 0.0, 0.0]))
        self.assertEqual(expected_completions, actual_completions)

    @ddt.data(True, False)
    def test_enabled_honors_waffle_switch(self, enabled):
        with self.override_completion_switch(enabled):
            self.assertEqual(self.completion_service.completion_tracking_enabled(), enabled)

    @ddt.data(
        (XBlockCompletionMode.COMPLETABLE, False, False, True),
        (XBlockCompletionMode.COMPLETABLE, True, False, False),
        (XBlockCompletionMode.COMPLETABLE, False, True, False),
        (XBlockCompletionMode.AGGREGATOR, False, False, False),
        (XBlockCompletionMode.EXCLUDED, False, False, False)
    )
    @ddt.unpack
    def test_can_mark_block_complete_on_view(self, mode, has_score, has_custom_completion, can_mark_complete):
        block = XBlock(Mock(), scope_ids=Mock(spec=ScopeIds))
        block.completion_mode = mode
        block.has_score = has_score
        if has_custom_completion:
            block.has_custom_completion = True

        self.assertEqual(self.completion_service.can_mark_block_complete_on_view(block), can_mark_complete)

    def test_blocks_to_mark_complete_on_view(self):

        completable_block_1 = XBlock(Mock(), scope_ids=Mock(spec=ScopeIds))
        usage_id_1 = UsageKey.from_string("i4x://edX/100/a/1").replace(course_key=self.course_key)
        completable_block_1.scope_ids.usage_id = usage_id_1
        completable_block_2 = XBlock(Mock(), scope_ids=Mock(spec=ScopeIds))
        usage_id_2 = UsageKey.from_string("i4x://edX/100/a/2").replace(course_key=self.course_key)
        completable_block_2.scope_ids.usage_id = usage_id_2
        aggregator_block = XBlock(Mock(), scope_ids=Mock(spec=ScopeIds))
        usage_id_3 = UsageKey.from_string("i4x://edX/100/a/3").replace(course_key=self.course_key)
        aggregator_block.scope_ids.usage_id = usage_id_3
        aggregator_block.completion_mode = XBlockCompletionMode.AGGREGATOR

        self.assertEqual(self.completion_service.blocks_to_mark_complete_on_view([]), [])

        self.assertEqual(
            self.completion_service.blocks_to_mark_complete_on_view([aggregator_block]), []
        )

        self.assertEqual(
            self.completion_service.blocks_to_mark_complete_on_view(
                [completable_block_1, completable_block_2, aggregator_block]
            ),
            [completable_block_1, completable_block_2]
        )

        BlockCompletion.objects.submit_completion(
            user=self.user,
            block_key=completable_block_2.scope_ids.usage_id,
            completion=1.0
        )

        self.assertEqual(
            self.completion_service.blocks_to_mark_complete_on_view(
                [completable_block_1, completable_block_2, aggregator_block]
            ),
            [completable_block_1]
        )

        BlockCompletion.objects.submit_completion(
            user=self.user,
            block_key=completable_block_1.scope_ids.usage_id,
            completion=1.0
        )

        self.assertEqual(
            self.completion_service.blocks_to_mark_complete_on_view(
                [completable_block_1, completable_block_2, aggregator_block]
            ),
            []
        )


@ddt.ddt
class CompletionDelayTestCase(CompletionSetUpMixin, TestCase):
    """
    Test that the completion-by-viewing delay is properly passed in from
    the project settings.
    """

    @ddt.data(1, 1000, 0)
    def test_get_complete_on_view_delay_ms(self, delay):
        service = CompletionService(self.user, self.context_key)
        with override_settings(COMPLETION_BY_VIEWING_DELAY_MS=delay):
            self.assertEqual(service.get_complete_on_view_delay_ms(), delay)
