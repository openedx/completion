"""
The unit tests for utilities.py.

"""


from django.test import TestCase
from opaque_keys.edx.keys import CourseKey

from ..exceptions import UnavailableCompletionData
from ..utilities import get_key_to_last_completed_block
from ..test_utils import UserFactory, CompletionSetUpMixin, submit_completions_for_testing


class TestCompletionUtilities(CompletionSetUpMixin, TestCase):
    """
    Tests methods in completion's external-facing API.
    """

    COMPLETION_SWITCH_ENABLED = True

    def setUp(self):
        super(TestCompletionUtilities, self).setUp()
        self.user = UserFactory.create()
        self.course_key = CourseKey.from_string("course-v1:edX+MOOC101+2049_T2")
        self.block_keys = [
            self.course_key.make_usage_key('video', str(number))
            for number in range(5)
        ]
        submit_completions_for_testing(self.user, self.block_keys)

    def test_can_get_key_to_last_completed_block(self):
        last_block_key = get_key_to_last_completed_block(
            self.user,
            self.course_key
        )

        expected_block_usage_key = self.course_key.make_usage_key(
            "video",
            str(4)
        )
        self.assertEqual(last_block_key, expected_block_usage_key)

    def test_getting_last_completed_course_block_in_untouched_enrollment_throws(self):
        course_key = CourseKey.from_string("edX/NotACourse/2049_T2")

        with self.assertRaises(UnavailableCompletionData):
            get_key_to_last_completed_block(self.user, course_key)
