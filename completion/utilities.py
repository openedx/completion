"""
File is the public API for BlockCompletion. It is the interface that prevents
external users from depending on the BlockCompletion model. Methods working with
the BlockCompletion model should be included here.

"""


from .exceptions import UnavailableCompletionData
from .models import BlockCompletion


def get_key_to_last_completed_block(user, context_key):
    """
    Returns the last block a "user" completed in a learning context such as a
    specific course (stated as "context_key").

    raises UnavailableCompletionData when the user has not completed blocks in
    the course.

    raises UnavailableCompletionData when the visual progress waffle flag is
    disabled.
    """

    last_completed_block = BlockCompletion.get_latest_block_completed(user, context_key)

    if last_completed_block is not None:
        return last_completed_block.block_key

    raise UnavailableCompletionData(context_key)
