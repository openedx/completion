'''
This file contains custom exceptions used by the completion repository.
'''
from __future__ import unicode_literals, absolute_import


class UnavailableCompletionData(Exception):
    '''
    UnavailableCompletionData should be raised when a method is unable to gather
    completion data from BlockCompletion.
    '''

    def __init__(self, course_key):
        Exception.__init__(
            self, "The learner does not have completion data within course {}".format(course_key))
