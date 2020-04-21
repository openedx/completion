"""
This file contains custom exceptions used by the completion repository.
'''

"""


class UnavailableCompletionData(Exception):
    """
    UnavailableCompletionData should be raised when a method is unable to gather
    completion data from BlockCompletion.
    """

    def __init__(self, context_key):
        Exception.__init__(
            self, "The learner does not have completion data within learning context {}".format(context_key))
