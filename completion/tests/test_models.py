"""
Test models, managers, and validators.
"""

from __future__ import absolute_import, division, unicode_literals

import datetime
from pytz import UTC

from django.core.exceptions import ValidationError
from django.test import TestCase

from freezegun import freeze_time
from opaque_keys.edx.keys import CourseKey, UsageKey

from .. import models
from ..test_utils import CompletionSetUpMixin, UserFactory, submit_completions_for_testing


class PercentValidatorTestCase(TestCase):
    """
    Test that validate_percent only allows floats (and ints) between 0.0 and 1.0.
    """

    def test_valid_percents(self):
        for value in [1.0, 0.0, 1, 0, 0.5, 0.333081348071397813987230871]:
            models.validate_percent(value)

    def test_invalid_percent(self):
        for value in [-0.00000000001, 1.0000000001, 47.1, 1000, None, float('inf'), float('nan')]:
            self.assertRaises(ValidationError, models.validate_percent, value)


class SubmitCompletionTestCase(CompletionSetUpMixin, TestCase):
    """
    Test that BlockCompletion.objects.submit_completion has the desired
    semantics.
    """
    COMPLETION_SWITCH_ENABLED = True

    def setUp(self):
        super(SubmitCompletionTestCase, self).setUp()
        self.set_up_completion()

    def test_changed_value(self):
        with self.assertNumQueries(4):  # Get, update, 2 * savepoints
            completion, isnew = models.BlockCompletion.objects.submit_completion(
                user=self.user,
                course_key=self.course_key,
                block_key=self.block_key,
                completion=0.9,
            )
        completion.refresh_from_db()
        self.assertEqual(completion.completion, 0.9)
        self.assertFalse(isnew)
        self.assertEqual(models.BlockCompletion.objects.count(), 1)

    def test_unchanged_value(self):
        with self.assertNumQueries(1):  # Get
            completion, isnew = models.BlockCompletion.objects.submit_completion(
                user=self.user,
                course_key=self.course_key,
                block_key=self.block_key,
                completion=0.5,
            )
        completion.refresh_from_db()
        self.assertEqual(completion.completion, 0.5)
        self.assertFalse(isnew)
        self.assertEqual(models.BlockCompletion.objects.count(), 1)

    def test_new_user(self):
        newuser = UserFactory()
        with self.assertNumQueries(4):  # Get, update, 2 * savepoints
            _, isnew = models.BlockCompletion.objects.submit_completion(
                user=newuser,
                course_key=self.course_key,
                block_key=self.block_key,
                completion=0.0,
            )
        self.assertTrue(isnew)
        self.assertEqual(models.BlockCompletion.objects.count(), 2)

    def test_new_block(self):
        newblock = UsageKey.from_string(u'block-v1:edx+test+run+type@video+block@puppers')
        with self.assertNumQueries(4):  # Get, update, 2 * savepoints
            _, isnew = models.BlockCompletion.objects.submit_completion(
                user=self.user,
                course_key=newblock.course_key,
                block_key=newblock,
                completion=1.0,
            )
        self.assertTrue(isnew)
        self.assertEqual(models.BlockCompletion.objects.count(), 2)

    def test_invalid_completion(self):
        with self.assertRaises(ValidationError):
            models.BlockCompletion.objects.submit_completion(
                user=self.user,
                course_key=self.block_key.course_key,
                block_key=self.block_key,
                completion=1.2
            )
        completion = models.BlockCompletion.objects.get(user=self.user, block_key=self.block_key)
        self.assertEqual(completion.completion, 0.5)
        self.assertEqual(models.BlockCompletion.objects.count(), 1)

    def test_submit_batch_completion(self):
        blocks = [(self.block_key, 1.0)]
        models.BlockCompletion.objects.submit_batch_completion(self.user, self.course_key, blocks)
        self.assertEqual(models.BlockCompletion.objects.count(), 1)
        self.assertEqual(models.BlockCompletion.objects.last().completion, 1.0)

    def test_submit_batch_completion_with_same_block_new_completion_value(self):
        self.assertEqual(models.BlockCompletion.objects.count(), 1)
        model = models.BlockCompletion.objects.first()
        self.assertEqual(model.completion, 0.5)
        blocks = [
            (UsageKey.from_string('block-v1:edx+test+run+type@video+block@doggos'), 1.0),
        ]
        models.BlockCompletion.objects.submit_batch_completion(self.user, self.course_key, blocks)
        self.assertEqual(models.BlockCompletion.objects.count(), 1)
        model = models.BlockCompletion.objects.first()
        self.assertEqual(model.completion, 1.0)


class CompletionDisabledTestCase(CompletionSetUpMixin, TestCase):
    """
    Test that completion is not track when the feature switch is disabled.
    """
    COMPLETION_SWITCH_ENABLED = False

    def setUp(self):
        super(CompletionDisabledTestCase, self).setUp()
        self.set_up_completion()

    def test_cannot_call_submit_completion(self):
        self.assertEqual(models.BlockCompletion.objects.count(), 1)
        with self.assertRaises(RuntimeError):
            models.BlockCompletion.objects.submit_completion(
                user=self.user,
                course_key=self.block_key.course_key,
                block_key=self.block_key,
                completion=0.9,
            )
        self.assertEqual(models.BlockCompletion.objects.count(), 1)

    def test_submit_batch_completion_without_waffle(self):
        with self.assertRaises(RuntimeError):
            blocks = [(self.block_key, 1.0)]
            models.BlockCompletion.objects.submit_batch_completion(self.user, self.course_key, blocks)


class CompletionFetchingTestCase(CompletionSetUpMixin, TestCase):
    """
    Test model methods:
        latest completion per course, and all completions per course
    """
    COMPLETION_SWITCH_ENABLED = True

    def setUp(self):
        super(CompletionFetchingTestCase, self).setUp()
        self.user_one = UserFactory.create()
        self.user_two = UserFactory.create()
        self.course_key_one = CourseKey.from_string("edX/MOOC101/2049_T2")
        self.course_key_two = CourseKey.from_string("edX/MOOC101/2050_T2")
        self.block_keys = [
            UsageKey.from_string("i4x://edX/MOOC101/video/{}".format(number)) for number in range(5)
        ]

        the_completion_date = datetime.datetime(2050, 1, 1, tzinfo=UTC)
        for idx, block_key in enumerate(self.block_keys[:3]):
            with freeze_time(the_completion_date):
                models.BlockCompletion.objects.submit_completion(
                    user=self.user_one,
                    course_key=self.course_key_one,
                    block_key=block_key,
                    completion=1.0 - (0.2 * idx),
                )
            the_completion_date += datetime.timedelta(days=1)

        # Wrong user
        submit_completions_for_testing(self.user_two, self.course_key_one, self.block_keys[2:])

        # Wrong course
        the_completion_date = datetime.datetime(2050, 1, 10, tzinfo=UTC)
        with freeze_time(the_completion_date):
            submit_completions_for_testing(self.user_one, self.course_key_two, [self.block_keys[4]])

    def test_get_course_completions_missing_runs(self):
        actual_completions = models.BlockCompletion.get_course_completions(self.user_one, self.course_key_one)
        expected_block_keys = [key.replace(course_key=self.course_key_one) for key in self.block_keys[:3]]
        expected_completions = dict(zip(expected_block_keys, [1.0, 0.8, 0.6]))
        self.assertEqual(expected_completions, actual_completions)

    def test_get_course_completions_empty_result_set(self):
        self.assertEqual(
            models.BlockCompletion.get_course_completions(self.user_two, self.course_key_two),
            {}
        )

    def test_get_latest_block_completed(self):
        self.assertEqual(
            models.BlockCompletion.get_latest_block_completed(self.user_one, self.course_key_one).block_key,
            self.block_keys[2]
        )

    def test_get_latest_completed_none_exist(self):
        self.assertIsNone(models.BlockCompletion.get_latest_block_completed(self.user_two, self.course_key_two))

    def test_latest_blocks_completed_all_courses(self):
        self.assertDictEqual(
            models.BlockCompletion.latest_blocks_completed_all_courses(self.user_one),
            {
                self.course_key_two: (datetime.datetime(2050, 1, 10, tzinfo=UTC), self.block_keys[4]),
                self.course_key_one: (datetime.datetime(2050, 1, 3, tzinfo=UTC), self.block_keys[2])
            }
        )
