completion
=============================

|pypi-badge| |CI| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge|

A library for tracking completion of blocks by learners in edX courses.

Overview
________

This repository provides a Django model `BlockCompletion` that is intended to be plugged into ``edx-platform``.  It
provides various handlers and services for the recording of completion data.  It also provides a DRF API for submitting
completion data in batches.

Enabling in the LMS
-------------------
By default, the Open edX LMS does not use this library. To turn it on, go to http://localhost:18000/admin/waffle/switch/ (substitute your LMS URL for http://localhost:18000/), and add a new switch with Name ``completion.enable_completion_tracking`` and Active selected.

See `Completion Tool <https://edx.readthedocs.io/projects/open-edx-building-and-running-a-course/en/latest/exercises_tools/completion.html>`_ in the Open edX documentation for details on what will happen once enabled.

License
-------

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see ``LICENSE.txt`` for details.

How To Contribute
-----------------

Contributions are very welcome.

Please read `How To Contribute <https://github.com/openedx/.github/blob/master/CONTRIBUTING.md>`_ for details.


PR description template should be automatically applied if you are sending PR from github interface; otherwise you
can find it it at `PULL_REQUEST_TEMPLATE.md <https://github.com/openedx/completion/blob/master/.github/PULL_REQUEST_TEMPLATE.md>`_

Issue report template should be automatically applied if you are sending it from github UI as well; otherwise you
can find it at `ISSUE_TEMPLATE.md <https://github.com/openedx/completion/blob/master/.github/ISSUE_TEMPLATE.md>`_

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@edx.org.

Using with Docker Devstack
--------------------------

Prerequisite: Have your Open edX `Devstack <https://github.com/openedx/devstack>`_ properly installed.

Note: When you see "from inside the lms" below, it means that you've run ``make lms-shell`` from your devstack
directory and are on a command prompt inside the LMS container.

#. Clone this repo into ``../src/`` directory (relative to your "devstack" repo location). This will mount the
   directory in a way that is accessible to the lms container.

#. From inside the lms, uninstall completion and reinstall your local copy. You can just copy the following line::

    pip uninstall completion -y; pip install -e /edx/src/completion/

#. Now, get your completion development environment set up::

    cd /edx/src/completion
    virtualenv completion-env
    source completion-env/bin/activate
    make install

#. Don't forget to enable the waffle switch as described above in "Enabling in the LMS"

#. That's it!  In order to simulate a given tox environment ``(django18, django111, quality)``, run ``tox -e <env>`` for the env in question.  If you want to run ``pytest`` directly::

    pytest completion/tests/test_models.py

Getting Help
------------

Have a question about this repository, or about Open edX in general?  Please
refer to this `list of resources`_ if you need any assistance.

.. _list of resources: https://open.edx.org/getting-help


.. |pypi-badge| image:: https://img.shields.io/pypi/v/edx-completion.svg
    :target: https://pypi.python.org/pypi/edx-completion/
    :alt: PyPI

.. |CI| image:: https://github.com/openedx/completion/workflows/Python%20CI/badge.svg?branch=master
    :target: https://github.com/openedx/completion/actions?query=workflow%3A%22Python+CI%22
    :alt: CI

.. |codecov-badge| image:: http://codecov.io/github/edx/completion/coverage.svg?branch=master
    :target: http://codecov.io/github/edx/completion?branch=master
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/completion/badge/?version=latest
    :target: http://completion.readthedocs.io/en/latest/
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/edx-completion.svg
    :target: https://pypi.python.org/pypi/edx-completion/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/edx/completion.svg
    :target: https://github.com/openedx/completion/blob/master/LICENSE.txt
    :alt: License
