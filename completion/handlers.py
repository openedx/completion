"""
Signal handlers to trigger completion updates.
"""

import logging

from django.contrib.auth.models import User
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import LearningContextKey, UsageKey
from xblock.completable import XBlockCompletionMode
from xblock.core import XBlock

from . import waffle
from .models import BlockCompletion

log = logging.getLogger(__name__)


def scorable_block_completion(sender, **kwargs):  # pylint: disable=unused-argument
    """
    When a problem is scored, submit a new BlockCompletion for that block.
    """
    if not waffle.waffle().is_enabled(waffle.ENABLE_COMPLETION_TRACKING):
        return
    try:
        block_key = UsageKey.from_string(kwargs['usage_id'])
    except InvalidKeyError:
        log.exception("Unable to parse XBlock usage_id for completion: %s", block_key)
        return

    if block_key.context_key.is_course and block_key.context_key.run is None:
        # In the case of old mongo courses, the context_key cannot be derived
        # from the block key alone since it will be missing run info:
        course_key_with_run = LearningContextKey.from_string(kwargs['course_id'])
        block_key = block_key.replace(course_key=course_key_with_run)

    block_cls = XBlock.load_class(block_key.block_type)
    if XBlockCompletionMode.get_mode(block_cls) != XBlockCompletionMode.COMPLETABLE:
        return
    if getattr(block_cls, 'has_custom_completion', False):
        return
    user = User.objects.get(id=kwargs['user_id'])
    if kwargs.get('score_deleted'):
        completion = 0.0
    else:
        completion = 1.0
    if not kwargs.get('grader_response'):
        BlockCompletion.objects.submit_completion(
            user=user,
            block_key=block_key,
            completion=completion,
        )
