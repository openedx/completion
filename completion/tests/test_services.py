"""
Tests of completion xblock runtime services
"""

from __future__ import unicode_literals

import ddt
from django.test import TestCase
from django.test.utils import override_settings
from opaque_keys.edx.keys import CourseKey, UsageKey

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

        self.completion_service = CompletionService(self.user, self.course_key)

        # Proper completions for the given runtime
        for idx, block_key in enumerate(self.block_keys[0:3]):
            BlockCompletion.objects.submit_completion(
                user=self.user,
                course_key=self.course_key,
                block_key=block_key,
                completion=1.0 - (0.2 * idx),
            )

        # Wrong user
        for idx, block_key in enumerate(self.block_keys[2:]):
            BlockCompletion.objects.submit_completion(
                user=self.other_user,
                course_key=self.course_key,
                block_key=block_key,
                completion=0.9 - (0.2 * idx),
            )

        # Wrong course
        BlockCompletion.objects.submit_completion(
            user=self.user,
            course_key=self.other_course_key,
            block_key=self.block_keys[4],
            completion=0.75,
        )

    def test_get_completion(self):
        actual_completions = self.completion_service.get_completions(self.block_keys)
        expected_completions = dict(zip(self.block_keys, [1.0, 0.8, 0.6, 0.0, 0.0]))
        self.assertEqual(expected_completions, actual_completions)

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


@ddt.ddt
class CompletionDelayTestCase(CompletionSetUpMixin, TestCase):
    """
    Test that the completion-by-viewing delay is properly passed in from
    the project settings.
    """

    @ddt.data(1, 1000, 0)
    def test_get_completion_by_viewing_delay_ms(self, delay):
        service = CompletionService(self.user, self.course_key)
        with override_settings(COMPLETION_BY_VIEWING_DELAY_MS=delay):
            self.assertEqual(service.get_completion_by_viewing_delay_ms(), delay)
