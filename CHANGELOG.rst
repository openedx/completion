Change Log
==========

..
   All enhancements and patches to completion will be documented
   in this file.  It adheres to the structure of http://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (http://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

[4.6.0] - 2024-4-16
-------------------

* Add support for Python 3.11 and 3.12

[4.5.0] - 2024-3-19
--------------------
* Added ``clear_learning_context_completion`` to enable clearing a learner's
  completion for a course

[4.4.1] - 2023-10-27
--------------------
* Fix RemovedInDjango41Warning by removing `django_app_config`

[4.4.0] - 2023-10-20
--------------------
* Added tracking logs for completion events

[4.3.0]- 2023-07-26
------------------------------------------------
* Added support for Django 4.2

[4.2.1]- 2023-04-26
------------------------------------------------
* Support ``get_child_blocks`` along with ``get_child_descriptors``.
* Switch from ``edx-sphinx-theme`` to ``sphinx-book-theme`` since the former is
  deprecated

[4.1.0]- 2021-07-19
------------------------------------------------
* Add Django 3.0, 3.1 & 3.2 Support

[4.0.4]- 2021-02-04
------------------------------------------------
* Update ``get_key_to_last_completed_block`` to return ``full_block_key`` instead of ``block_key``

[4.0.2] - 2021-02-04
------------------------------------------------
* Future-proof usage of ``edx_toggles.toggles``


[4.0.1] - 2021-01-05
------------------------------------------------
* Replace reference to deprecated import path ``student.models``
  with ``common.djangoapps.student.models``.
* Updated the build status badge in README.rst to point to travis-ci.com instead of travis-ci.org


[4.0.0] - 2020-11-05
------------------------------------------------
* Remove soon-to-be-deprecated WaffleSwitchNamespace class instances
* BACKWARD INCOMPATIBLE: Removes ``waffle()``, which returned a (now deprecated) WaffleSwitchNamespace. This should only affect tests in edx-platform.
* Requires edx-toggles>=1.2.0, which introduces a new API to waffle objects.
* Refactors ``ENABLE_COMPLETION_TRACKING_SWITCH`` from a ``LegacyWaffleSwitch`` to the updated ``WaffleSwitch``.  We don't expect uses of this updated switch to require changes, unless there are surprise uses of deprecated methods from ``LegacyWaffleSwitch``.

[3.2.5] - 2020-10-23
------------------------------------------------
* Fix waffle switch override in tests by relying on newest edx_toggles API

[3.2.4] - 2020-07-21
------------------------------------------------
* Fix AttributeError raised by `vertical_is_complete`.
  * by ensuring `get_completable_children` doesn't return null

[3.2.3] - 2020-07-01
------------------------------------------------
* Updated the children lookup for `vertical_is_complete` to utilize the XBlockCompletion model. There are
  three completion modes to consider: EXCLUDED, AGGREGATOR, COMPLETABLE.

  * This method will now ignore any block with XBlockCompletion.EXCLUDED.
  * This method will now recurse down any child of a vertical if that child has XBlockCompletion.AGGREGATOR.
  * This method will consider all children blocks with XBlockCompletion.COMPLETABLE as candidates to
    determine if the vertical is complete.

[3.2.2] - 2020-06-30
------------------------------------------------
* Adding recursive lookup for children of a vertical to the `vertical_is_complete` method in services.py.

  * This was added because verticals containing children that had their own children were not being properly marked
    as complete. Since the vertical was only looking one layer deep, it was possible to have children lower in the tree
    incomplete, but the vertical would still be marked as complete. Now it looks at all leaves under the vertical.

[3.1.1] - 2020-02-24
------------------------------------------------
* Remove unnecessary constraint for edx-drf-extensions<3.0.0

[3.1.0] - 2020-02-18
------------------------------------------------
* Upgrades packages, drops support for Python 2.

[3.0.1] - 2019-10-22
------------------------------------------------
* Fix the package long description to be valid rST, check this in CI.

[3.0.0] - 2019-10-22
------------------------------------------------
* Support tracking completion of XBlocks in any "learning context", such as in
  a content library, and not just in courses. To keep the code clean, this has
  been done as a **breaking change** to the python API. (The API has been
  simplified so that it's generally only necessary to pass in a block key /
  usage key rather than block key + course key.) The REST API is unchanged.

[2.1.1] - 2019-10-21
------------------------------------------------
* Updated credentials for PyPI deployment via token.

[2.1.0] - 2019-10-18
------------------------------------------------
* Switch blocks_to_mark_complete_on_view() to return a list of XBlocks instead of a set.  Many XBlocks aren't hashable;
  the old implementation allowed subtle bugs under Python 2.7 but triggers an immediate error under 3.5.

[2.0.0] - 2019-04-23
------------------------------------------------
* Unpin django-rest-framework requirements. This is a potentially **breaking change** if people were
  relying on this package to ensure the correct version of djangorestframework was being installed.
* Remove the AUTHORS file and references to it.

[1.0.2] - 2019-03-11
------------------------------------------------

* Fix the 403 error occurring for completion-batch API for requests coming from the iOS devices

[1.0.0] - 2018-10-16
------------------------------------------------
* Updated edx-drf-extensions imports. Completion will no longer work with
  outdated versions of edx-drf-extensions.

[0.1.14] - 2018-10-04
------------------------------------------------
* Added submit_completion and submit_group_completion methods on
  CompletionService.

[0.1.7] - 2018-06-18
------------------------------------------------
* Added can_mark_block_complete_on_view() and blocks_to_mark_complete_on_view()
  methods on CompletionService and renamed get_completion_by_viewing_delay_ms()
  to get_complete_on_view_delay_ms().

[0.1.6] - 2018-04-13
------------------------------------------------
* Remove usage of deprecated CourseStructure api.

[0.1.5] - 2018-04-03
------------------------------------------------
* Delete enable_visual_progress methods and checks. Deprecate ENABLE_VISUAL_PROGRESS,
  ENABLE_COURSE_VISUAL_PROGRESS, and ENABLE_SITE_VISUAL_PROGRESS waffle flags

[0.1.4] - 2018-03-28
------------------------------------------------
* Site configurations must now explicitly disable visual progress for the
  enable_visual_progress() feature gating function to return False early.

[0.1.3] - 2018-03-26
------------------------------------------------
* Added some documentation.

[0.1.2] - 2018-03-23
------------------------------------------------
* Fix management of dependency versions

[0.1.1] - 2018-03-23
------------------------------------------------
* Fixes wildly inefficient raw query in BlockCompletion.latest_blocks_completed_all_courses()
* Updates freezegun version, makes tests that use it somewhat faster.

[0.1.0] - 2018-03-20
------------------------------------------------
* Fixes https://openedx.atlassian.net/browse/EDUCATOR-2540

[0.0.11] - 2018-03-20
------------------------------------------------
* Added "subsection-completion/{username}/{course_key}/{subsection_id}" API
  endpoint, to be used with the completion milestones experiment.

[0.0.9] - 2018-02-27
------------------------------------------------
* Added "utilities.py", which houses methods for working with BlockCompletion
  data.

[0.0.8] - 2018-03-01
------------------------------------------------
* Add model method for superlative “last completed block” - for site awareness
  include every last completed block by course, for later sorting in business
  layer.

[0.0.7] - 2018-02-15
------------------------------------------------
* Add settings and service method for determining completion-by-viewing delay.

[0.0.6] - 2018-02-13
------------------------------------------------
* Add the additional completion logic into the service and models from edx-platform

[0.0.2] - 2018-01-31
------------------------------------------------
* Fix up edx-lint requirements shenanigans.

[0.0.1] - 2018-01-31
------------------------------------------------
* Initial release
