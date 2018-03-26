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
