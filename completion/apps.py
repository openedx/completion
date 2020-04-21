"""
App Configuration for Completion
"""


from django.apps import AppConfig


class CompletionAppConfig(AppConfig):
    """
    App Configuration for Completion
    """
    name = 'completion'
    verbose_name = 'Completion'

    plugin_app = {
        'url_config': {
            'lms.djangoapp': {
                'namespace': 'completion',
                'regex': r'^api/completion/',
                'relative_path': 'api.urls',
            },
        },
        'settings_config': {
            'lms.djangoapp': {
                'common': {
                    'relative_path': 'settings.common',
                },
            },
        },
        'signals_config': {
            'lms.djangoapp': {
                'relative_path': 'handlers',
                'receivers': [
                    {
                        'receiver_func_name': 'scorable_block_completion',
                        'signal_path': 'lms.djangoapps.grades.signals.signals.PROBLEM_WEIGHTED_SCORE_CHANGED',
                        'dispatch_uid': 'completion.handlers.scorable_block_completion',
                    },
                ],
            },
        },
    }
