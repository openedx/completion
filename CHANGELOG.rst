Change Log
----------

..
   All enhancements and patches to completion will be documented
   in this file.  It adheres to the structure of http://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (http://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
~~~~~~~~~~

[1.0.0] - 2018-10-16
--------------------
* Updated edx-drf-extensions imports. Completion will no longer work with
  outdated versions of edx-drf-extensions.

[0.1.14] - 2018-10-04
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Added submit_completion and submit_group_completion methods on 
  CompletionService.

[0.1.7] - 2018-06-18
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Added can_mark_block_complete_on_view() and blocks_to_mark_complete_on_view()
methods on CompletionService and renamed get_completion_by_viewing_delay_ms()
to get_complete_on_view_delay_ms().

[0.1.6] - 2018-04-13
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Remove usage of deprecated CourseStructure api.

[0.1.5] - 2018-04-03
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Delete enable_visual_progress methods and checks. Deprecate ENABLE_VISUAL_PROGRESS,
ENABLE_COURSE_VISUAL_PROGRESS, and ENABLE_SITE_VISUAL_PROGRESS waffle flags

[0.1.4] - 2018-03-28
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Site configurations must now explicitly disable visual progress for the
  enable_visual_progress() feature gating function to return False early.

[0.1.3] - 2018-03-26
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Added some documentation.

[0.1.2] - 2018-03-23
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Fix management of dependency versions

[0.1.1] - 2018-03-23
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Fixes wildly inefficient raw query in BlockCompletion.latest_blocks_completed_all_courses()
* Updates freezegun version, makes tests that use it somewhat faster.

[0.1.0] - 2018-03-20
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Fixes https://openedx.atlassian.net/browse/EDUCATOR-2540

[0.0.11] - 2018-03-20
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Added "subsection-completion/{username}/{course_key}/{subsection_id}" API
  endpoint, to be used with the completion milestones experiment.

[0.0.9] - 2018-02-27
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Added "utilities.py", which houses methods for working with BlockCompletion
  data.

[0.0.8] - 2018-03-01
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Add model method for superlative “last completed block” - for site awareness 
  include every last completed block by course, for later sorting in business 
  layer.

[0.0.7] - 2018-02-15
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Add settings and service method for determining completion-by-viewing delay.

[0.0.6] - 2018-02-13
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Add the additional completion logic into the service and models from edx-platform

[0.0.2] - 2018-01-31
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Fix up edx-lint requirements shenanigans.

[0.0.1] - 2018-01-31
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Initial release
