"""
Runtime service for communicating completion information to the xblock system.
"""

from django.conf import settings
from django.contrib.auth.models import User
from xblock.completable import XBlockCompletionMode

from .models import BlockCompletion
from . import waffle


class CompletionService:
    """
    Service for handling completions for a user within a learning context.

    Exposes

    * self.completion_tracking_enabled() -> bool
    * self.get_completions(candidates)
    * self.vertical_is_complete(vertical_item)

    Constructor takes a user object and context_key as arguments.
    """

    def __init__(self, user, context_key):
        self._user = user
        self._context_key = context_key

    def completion_tracking_enabled(self):
        """
        Exposes ENABLE_COMPLETION_TRACKING waffle switch to XModule runtime

        Return value:

            bool -> True if completion tracking is enabled.
        """
        return waffle.waffle().is_enabled(waffle.ENABLE_COMPLETION_TRACKING)

    def get_completions(self, candidates):
        """
        Given an iterable collection of block_keys in the learning context,
        returns a mapping of the block_keys to the present completion values of
        their associated blocks.

        If a completion is not found for a given block in the current context,
        0.0 is returned.  The service does not attempt to verify that the block
        exists within the learning context.

        Parameters:

            candidates: collection of BlockKeys within the current learning context.
            Note: Usage keys may not have the course run filled in for old mongo courses.
            This method checks for completion records against a set of BlockKey candidates with the course run
            filled in from self._context_key.

        Return value:

            dict[BlockKey] -> float: Mapping blocks to their completion value.
        """
        queryset = BlockCompletion.user_learning_context_completion_queryset(self._user, self._context_key).filter(
            # pylint: disable=no-member
            block_key__in=candidates
        )
        completions = BlockCompletion.completion_by_block_key(queryset)

        def fill_in_run(block_key):
            """ Add run information to the block usage keys, if it's missing (old mongo keys) """
            if block_key.context_key.is_course and block_key.context_key.run is None:
                return block_key.replace(course_key=self._context_key)
            return block_key

        candidates_with_runs = [fill_in_run(candidate) for candidate in candidates]
        for candidate in candidates_with_runs:
            if candidate not in completions:
                completions[candidate] = 0.0
        return completions

    def get_completable_children(self, node):
        """
        Verticals will sometimes have children that also have children (some
        examples are content libraries, split tests, conditionals, etc.). This
        function will recurse through the children to get to the bottom leaf
        and return only those children. This function heavily utilizes the
        XBlockCompletionMode class to determine if it should recurse or not. It
        will only recurse if the node is an AGGREGATOR

        Note: The nodes passed in should have already taken the user into
        account so the proper blocks are shown for this user.
        """
        user_children = []
        mode = XBlockCompletionMode.get_mode(node)
        if mode == XBlockCompletionMode.AGGREGATOR:
            node_children = ((hasattr(node, 'get_child_descriptors') and node.get_child_descriptors())
                             or (hasattr(node, 'get_children') and node.get_children()))
            for child in node_children:
                user_children.extend(self.get_completable_children(child))
        elif node and mode == XBlockCompletionMode.COMPLETABLE:
            user_children = [node]
        return user_children

    def vertical_is_complete(self, item):
        """
        Calculates and returns whether a particular vertical is complete.
        The logic in this method is temporary, and will go away once the
        completion API is able to store a first-order notion of completeness
        for parent blocks (right now it just stores completion for leaves-
        problems, HTML, video, etc.).
        """
        if item.scope_ids.block_type != 'vertical':
            raise ValueError('The passed in xblock is not a vertical type!')

        if not self.completion_tracking_enabled():
            return None

        # this is temporary local logic and will be removed when the whole course tree is included in completion
        child_locations = [child.scope_ids.usage_id for child in self.get_completable_children(item)]
        completions = self.get_completions(child_locations)
        for child_location in child_locations:
            if completions[child_location] < 1.0:
                return False
        return True

    def get_complete_on_view_delay_ms(self):
        """
        Do not mark blocks complete-on-view until they have been visible for
        the returned amount of time, in milliseconds.  Defaults to 5000.
        """
        return getattr(settings, 'COMPLETION_BY_VIEWING_DELAY_MS', 5000)

    def can_mark_block_complete_on_view(self, block):
        """
        Returns True if the xblock can be marked complete on view.
        This is true of any non-customized, non-scorable, completable block.
        """
        return (XBlockCompletionMode.get_mode(block) == XBlockCompletionMode.COMPLETABLE
                and not getattr(block, 'has_custom_completion', False)
                and not getattr(block, 'has_score', False)
                )

    def blocks_to_mark_complete_on_view(self, blocks):
        """
        Returns a list of blocks which should be marked complete on view and haven't been yet.
        """
        blocks = [block for block in blocks if self.can_mark_block_complete_on_view(block)]
        completions = self.get_completions({block.scope_ids.usage_id for block in blocks})
        return [block for block in blocks if completions.get(block.scope_ids.usage_id, 0) < 1.0]

    def submit_group_completion(self, block_key, completion, users=None, user_ids=None):
        """
        Submit a completion for a group of users.

        Arguments:

            block_key (opaque_key.edx.keys.UsageKey): The block to submit completions for.
            completion (float): A value in the range [0.0, 1.0]
            users ([django.contrib.auth.models.User]): An optional iterable of Users that completed the block.
            user_ids ([int]): An optional iterable of ids of Users that completed the block.

        Returns a list of (BlockCompletion, bool) where the boolean indicates
        whether the given BlockCompletion was newly created.
        """
        if users is None:
            users = []
        if user_ids is None:
            user_ids = []
        more_users = User.objects.filter(id__in=user_ids)
        if len(more_users) < len(user_ids):
            found_ids = {u.id for u in more_users}
            not_found_ids = [pk for pk in user_ids if pk not in found_ids]
            raise User.DoesNotExist("User not found with id(s): {}".format(not_found_ids))
        users.extend(more_users)

        submitted = []
        for user in users:
            submitted.append(BlockCompletion.objects.submit_completion(
                user=user,
                block_key=block_key,
                completion=completion
            ))
        return submitted

    def submit_completion(self, block_key, completion):
        """
        Submit a completion for the service user and course.

        Returns a (BlockCompletion, bool) where the boolean indicates
        whether the given BlockCompletion was newly created.
        """
        return BlockCompletion.objects.submit_completion(
            user=self._user,
            block_key=block_key,
            completion=completion
        )
