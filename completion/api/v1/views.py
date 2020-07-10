"""
API v1 views.
"""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import ugettext as _
from django.db import DatabaseError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status

# pylint: disable=ungrouped-imports
try:
    from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
except ImportError:
    from edx_rest_framework_extensions.authentication import JwtAuthentication

try:
    from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
except ImportError:
    from edx_rest_framework_extensions.authentication import SessionAuthenticationAllowInactiveUser
# pylint: enable=ungrouped-imports

from opaque_keys.edx.keys import LearningContextKey, UsageKey
from opaque_keys import InvalidKeyError

try:
    from student.models import CourseEnrollment
    from lms.djangoapps.course_api.blocks.api import get_blocks
    from openedx.core.lib.api.authentication import BearerAuthenticationAllowInactiveUser
except ImportError:
    pass

from completion import waffle
from completion.api.permissions import IsStaffOrOwner, IsUserInUrl
from completion.models import BlockCompletion


class CompletionBatchView(APIView):
    """
    Handles API requests to submit batch completions.
    """
    authentication_classes = (
        JwtAuthentication, BearerAuthenticationAllowInactiveUser, SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated, IsStaffOrOwner,)
    REQUIRED_KEYS = ['username', 'course_key', 'blocks']

    def _validate_and_parse(self, batch_object):
        """
        Performs validation on the batch object to make sure it is in the proper format.

        Parameters:
            * batch_object: The data provided to a POST. The expected format is the following:
            ```
            {
                "username": "username",
                "course_key": "context-key",
                "blocks": {
                    "block_key1": 0.0,
                    "block_key2": 1.0,
                    "block_key3": 1.0,
                }
            }
            ```

        Return Value:
            * tuple: (User, LearningContextKey, List of tuples (UsageKey, completion_float)

        Raises:

            django.core.exceptions.ValidationError:
                If any aspect of validation fails a ValidationError is raised.

            ObjectDoesNotExist:
                If a database object cannot be found an ObjectDoesNotExist is raised.
        """
        if not waffle.waffle().is_enabled(waffle.ENABLE_COMPLETION_TRACKING):
            raise ValidationError(
                _("BlockCompletion.objects.submit_batch_completion should not be called when the feature is disabled.")
            )

        for key in self.REQUIRED_KEYS:
            if key not in batch_object:
                raise ValidationError(_("Key '{key}' not found.").format(key=key))

        username = batch_object['username']
        user = User.objects.get(username=username)

        context_key_obj = self._validate_and_parse_context_key(batch_object['course_key'])

        if context_key_obj.is_course and not CourseEnrollment.is_enrolled(user, context_key_obj):
            raise ValidationError(_('User is not enrolled in course.'))

        blocks = batch_object['blocks']
        block_objs = []
        for block_key in blocks:
            block_key_obj = self._validate_and_parse_block_key(block_key, context_key_obj)
            completion = float(blocks[block_key])
            block_objs.append((block_key_obj, completion))

        return user, block_objs

    def _validate_and_parse_context_key(self, context_key):
        """
        Returns a validated parsed LearningContextKey deserialized from the given context_key.
        """
        try:
            return LearningContextKey.from_string(context_key)
        except InvalidKeyError:
            raise ValidationError(_("Invalid learning context key: {}").format(context_key))

    def _validate_and_parse_block_key(self, block_key, context_key_obj):
        """
        Returns a validated, parsed UsageKey deserialized from the given block_key.
        """
        try:
            block_key_obj = UsageKey.from_string(block_key)
        except InvalidKeyError:
            raise ValidationError(_("Invalid block key: {}").format(block_key))

        if block_key_obj.context_key.is_course and block_key_obj.context_key.run is None:
            # block_key_obj is from an old mongo course and its context_key is missing run info:
            block_key_obj = block_key_obj.replace(course_key=context_key_obj)

        if block_key_obj.context_key != context_key_obj:
            raise ValidationError(
                _("Block with key: '{key}' is not in context {context}").format(key=block_key, context=context_key_obj)
            )

        return block_key_obj

    def post(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Inserts a batch of completions.

        REST Endpoint Format:
        ```
        {
          "username": "username",
          "course_key": "course-key",
          "blocks": {
            "block_key1": 0.0,
            "block_key2": 1.0,
            "block_key3": 1.0,
          }
        }
        ```

        **Returns**

        A Response object, with an appropriate status code.

        If successful, status code is 200.
        ```
        {
           "detail" : _("ok")
        }
        ```

        Otherwise, a 400 or 404 may be returned, and the "detail" content will explain the error.

        """
        batch_object = request.data or {}
        try:
            user, blocks = self._validate_and_parse(batch_object)
            BlockCompletion.objects.submit_batch_completion(user, blocks)
        except ValidationError as exc:
            return Response({
                "detail": _(' ').join(str(msg) for msg in exc.messages),  # pylint: disable=exception-escape
            }, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as exc:
            return Response({
                "detail": str(exc),
            }, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as exc:
            return Response({
                "detail": str(exc),
            }, status=status.HTTP_404_NOT_FOUND)
        except DatabaseError as exc:
            return Response({
                "detail": str(exc),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"detail": _("ok")}, status=status.HTTP_200_OK)


class SubsectionCompletionView(APIView):
    """
    Handles API endpoints for the milestones experiments.
    TODO: EDUCATOR-2358 Remove this class after the
    milestones experiment is no longer running.
    """
    authentication_classes = (JwtAuthentication, SessionAuthenticationAllowInactiveUser,)
    permission_classes = (permissions.IsAuthenticated, IsUserInUrl)

    def get(self, request, username, course_key, subsection_id):
        """
        Returns completion for a (user, subsection, course).
        """

        def get_completion(course_completions, all_blocks, block_id):
            """
            Recursively get the aggregate completion for a subsection,
            given the subsection block and a list of all blocks.

            Parameters:
                course_completions: a dictionary of completion values by block IDs
                all_blocks: a dictionary of the block structure for a subsection
                block_id: an ID of a block for which to get completion
            """
            block = all_blocks.get(block_id)
            child_ids = block.get('children', [])
            if not child_ids:
                return course_completions.get(block.serializer.instance, 0)

            completion = 0
            total_children = 0
            for child_id in child_ids:
                completion += get_completion(course_completions, all_blocks, child_id)
                total_children += 1

            return int(completion == total_children)

        user_id = User.objects.get(username=username).id
        block_types_filter = [
            'course',
            'chapter',
            'sequential',
            'vertical',
            'html',
            'problem',
            'video',
            'discussion',
            'drag-and-drop-v2'
        ]

        blocks = get_blocks(
            request,
            UsageKey.from_string(subsection_id),
            nav_depth=2,
            requested_fields=[
                'children'
            ],
            block_types_filter=block_types_filter
        )

        course_key = LearningContextKey.from_string(course_key)
        context_completions = BlockCompletion.get_learning_context_completions(user_id, course_key)
        aggregated_completion = get_completion(context_completions, blocks['blocks'], blocks['root'])

        return Response({"completion": aggregated_completion}, status=status.HTTP_200_OK)
