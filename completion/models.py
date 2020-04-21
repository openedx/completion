"""
Completion tracking and aggregation models.
"""

import logging

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction
from django.utils.translation import ugettext as _

from model_utils.models import TimeStampedModel

from opaque_keys.edx.django.models import LearningContextKeyField, UsageKeyField

from . import waffle

log = logging.getLogger(__name__)

# pylint: disable=ungrouped-imports
try:
    from django.models import BigAutoField  # New in django 1.10
except ImportError:
    from .fields import BigAutoField


# pylint: enable=ungrouped-imports


def validate_percent(value):
    """
    Verify that the passed value is between 0.0 and 1.0.
    """
    if (value is None) or (not 0.0 <= value <= 1.0):
        raise ValidationError(_('{value} must be between 0.0 and 1.0').format(value=value))


class BlockCompletionManager(models.Manager):
    """
    Custom manager for BlockCompletion model.

    Adds submit_completion and submit_batch_completion methods.
    """

    def submit_completion(self, user, block_key, completion):
        """
        Update the completion value for the specified record.

        Parameters:
            * user (django.contrib.auth.models.User): The user for whom the
              completion is being submitted.
            * block_key (opaque_keys.edx.keys.UsageKey): The block that has had
              its completion changed. Note: if the block key is for an old mongo
              course, it must have had its 'run' information added via
              block_key = block_key.replace(
                  course_key=modulestore().fill_in_run(block_key.course_key)
              )
            * completion (float in range [0.0, 1.0]): The fractional completion
              value of the block (0.0 = incomplete, 1.0 = complete).

        Return Value:
            (BlockCompletion, bool): A tuple comprising the created or updated
            BlockCompletion object and a boolean value indicating whether the
            object was newly created by this call.

        Raises:

            ValueError:
                If the wrong type is passed for one of the parameters.

            django.core.exceptions.ValidationError:
                If a float is passed that is not between 0.0 and 1.0.

            django.db.DatabaseError:
                If there was a problem getting, creating, or updating the
                BlockCompletion record in the database.

                This will also be a more specific error, as described here:
                https://docs.djangoproject.com/en/1.11/ref/exceptions/#database-exceptions.
                IntegrityError and OperationalError are relatively common
                subclasses.
        """

        try:
            context_key = block_key.context_key
            block_type = block_key.block_type
        except AttributeError:
            raise ValueError(
                "block_key must be an instance of `opaque_keys.edx.keys.UsageKey`.  Got {}".format(type(block_key))
            )
        if context_key.is_course and context_key.run is None:
            raise ValueError(
                "If block_key is an old mongo key, you must add its run information to the key before calling "
                "submit_completion():\n"
                "block_key = block_key.replace(course_key=modulestore().fill_in_run(block_key.course_key))"
            )

        if waffle.waffle().is_enabled(waffle.ENABLE_COMPLETION_TRACKING):
            try:
                with transaction.atomic():
                    obj, is_new = self.get_or_create(  # pylint: disable=unpacking-non-sequence
                        user=user,
                        context_key=context_key,
                        block_key=block_key,
                        defaults={
                            'completion': completion,
                            'block_type': block_type,
                        },
                    )
            except IntegrityError:
                # The completion was created concurrently by another process
                log.info(
                    "An IntegrityError was raised when trying to create a BlockCompletion for %s:%s:%s.  "
                    "Falling back to get().",
                    user,
                    context_key,
                    block_key,
                )
                obj = self.get(
                    user=user,
                    context_key=context_key,
                    block_key=block_key,
                )
                is_new = False
            if not is_new and obj.completion != completion:
                obj.completion = completion
                obj.full_clean()
                obj.save(update_fields={'completion', 'modified'})
        else:
            # If the feature is not enabled, this method should not be called.
            # Error out with a RuntimeError.
            raise RuntimeError(
                "BlockCompletion.objects.submit_completion should not be \
                called when the feature is disabled."
            )
        return obj, is_new

    @transaction.atomic()
    def submit_batch_completion(self, user, blocks):
        """
        Performs a batch insertion of completion objects.

        Parameters:
            * user (django.contrib.auth.models.User): The user for whom the
              completions are being submitted.
            * blocks: A list of tuples of UsageKey to float completion values.
              (float in range [0.0, 1.0]): The fractional completion
              value of the block (0.0 = incomplete, 1.0 = complete).

        Return Value:
            Dict of (BlockCompletion, bool): A dictionary with a
            BlockCompletion object key and a value of bool. The boolean value
            indicates whether the object was newly created by this call.

        Raises:

            ValueError:
                If the wrong type is passed for one of the parameters.

            django.core.exceptions.ValidationError:
                If a float is passed that is not between 0.0 and 1.0.

            django.db.DatabaseError:
                If there was a problem getting, creating, or updating the
                BlockCompletion record in the database.
        """
        block_completions = {}
        for block, completion in blocks:
            (block_completion, is_new) = self.submit_completion(user, block, completion)
            block_completions[block_completion] = is_new
        return block_completions


# pylint: disable=model-has-unicode
class BlockCompletion(TimeStampedModel, models.Model):
    """
    Track completion of completable blocks.

    A completion is unique for each (user, context_key, block_key).

    The block_type field is included separately from the block_key to
    facilitate distinct aggregations of the completion of particular types of
    block.

    The completion value is stored as a float in the range [0.0, 1.0], and all
    calculations are performed on this float, though current practice is to
    only track binary completion, where 1.0 indicates that the block is
    complete, and 0.0 indicates that the block is incomplete.
    """
    id = BigAutoField(primary_key=True)  # pylint: disable=invalid-name
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    context_key = LearningContextKeyField(max_length=255, db_column="course_key")

    # note: this usage key may not have the run filled in for
    # old mongo courses.  Use the full_block_key property
    # instead when you want to use/compare the usage_key.
    block_key = UsageKeyField(max_length=255)
    block_type = models.CharField(max_length=64)
    completion = models.FloatField(validators=[validate_percent])

    objects = BlockCompletionManager()

    @property
    def full_block_key(self):
        """
        Returns the "correct" usage key value with the run filled in.
        This is only necessary for block keys from old mongo courses, which
        didn't include the run information in the block usage key.
        """
        if self.block_key.context_key.is_course and self.block_key.run is None:
            # pylint: disable=unexpected-keyword-arg, no-value-for-parameter
            return self.block_key.replace(course_key=self.context_key)
        return self.block_key

    @classmethod
    def get_learning_context_completions(cls, user, context_key):
        """
        Returns a dictionary mapping BlockKeys to completion values for all
        BlockCompletion records for the given user and learning context key.

        Return value:
            dict[BlockKey] = float
        """
        user_completions = cls.user_learning_context_completion_queryset(user, context_key)
        return cls.completion_by_block_key(user_completions)

    @classmethod
    def user_learning_context_completion_queryset(cls, user, context_key):
        """
        Returns a Queryset of completions for a given user and context_key.
        """
        return cls.objects.filter(user=user, context_key=context_key)

    @classmethod
    def latest_blocks_completed_all_courses(cls, user):
        """
        Returns a dictionary mapping course_keys to a tuple containing
        the block_key and modified time of the most recently modified
        completion for the course.

        This only returns results for courses and not other learning context
        types.

        Return value:
            {course_key: (modified_date, block_key)}
        """

        # Per the Django docs, dictionary params are not supported with the SQLite backend;
        # with this backend, you must pass parameters as a list. We use SQLite for unit tests,
        # so the same parameter is included twice in the parameter list below, rather than
        # including it in a dictionary once.
        latest_completions_by_course = cls.objects.raw(
            '''
            SELECT
                cbc.id AS id,
                cbc.course_key AS course_key,
                cbc.block_key AS block_key,
                cbc.modified AS modified
            FROM
                completion_blockcompletion cbc
            JOIN (
                SELECT
                     course_key,
                     MAX(modified) AS modified
                FROM
                     completion_blockcompletion
                WHERE
                     user_id = %s
                GROUP BY
                     course_key
            ) latest
            ON
                cbc.course_key = latest.course_key AND
                cbc.modified = latest.modified
            WHERE
                user_id = %s
            ;
            ''',
            [user.id, user.id]
        )
        try:
            return {
                completion.context_key: (completion.modified, completion.block_key)
                for completion in latest_completions_by_course
                if completion.context_key.is_course
            }
        except KeyError:
            # Iteration of the queryset above will always fail
            # with a KeyError if the queryset is empty
            return {}

    @classmethod
    def get_latest_block_completed(cls, user, context_key):
        """
        Returns a BlockCompletion Object for the last modified user/context_key mapping,
        or None if no such BlockCompletion exists.

        Return value:
            obj: block completion
        """
        try:
            latest_block_completion = cls.user_learning_context_completion_queryset(user,
                                                                                    context_key).latest()  # pylint: disable=no-member
        except cls.DoesNotExist:
            return None
        return latest_block_completion

    @staticmethod
    def completion_by_block_key(completion_iterable):
        """
        Return value:
            A dict mapping the full block key of a completion record to the completion value
            for each BlockCompletion object given in completion_iterable.  Each BlockKey is
            corrected to have the run field filled in via the BlockCompletion.context_key field.
        """
        return {completion.full_block_key: completion.completion for completion in completion_iterable}

    class Meta:
        index_together = [
            ('context_key', 'block_type', 'user'),
            ('user', 'context_key', 'modified'),
        ]

        unique_together = [
            ('context_key', 'block_key', 'user')
        ]
        get_latest_by = 'modified'

    def __unicode__(self):
        return 'BlockCompletion: {username}, {context_key}, {block_key}: {completion}'.format(
            username=self.user.username,
            context_key=self.context_key,
            block_key=self.block_key,
            completion=self.completion,
        )
