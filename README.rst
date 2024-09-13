completion
##########

|pypi-badge| |ci-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge| |status-badge|

Purpose
*******

A library for tracking completion of blocks by learners in Open edX courses.

This repository provides a Django model `BlockCompletion` that is intended to be plugged into ``edx-platform``.  It
provides various handlers and services for the recording of completion data.  It also provides a DRF API for submitting
completion data in batches.

Enabling in the LMS
*******************

By default, the Open edX LMS does not use this library. To turn it on, go to http://your.lms.site/admin/waffle/switch/, and add a new switch with Name ``completion.enable_completion_tracking`` and Active selected.

See `Completion Tool <https://edx.readthedocs.io/projects/open-edx-building-and-running-a-course/en/latest/exercises_tools/completion.html>`_ in the Open edX documentation for details on what will happen once enabled.

Getting Started with Development
********************************

Please see the Open edX documentation for `guidance on Python development <https://docs.openedx.org/en/latest/developers/how-tos/get-ready-for-python-dev.html>`_ in this repo.

To install the ``completion`` app, run these commands from the `completion` root directory:

.. code:: bash

    pip install -e


To run the test suite:

.. code:: bash

    pip install tox
    tox # to run only a single environment, do e.g. tox -e py312-django42-drflatest


To use a Django shell to test commands:

.. code:: bash

    make install
    python manage.py migrate
    python manage.py shell
    >>> from completion.models import BlockCompletion
    >>> <other commands...>


Deploying
*********

Tagged versions of the completion library are released to pypi.org.

To use the latest release in your project, add the following to your pip requirements file:

.. code:: bash

    edx-completion

Getting Help
************

Documentation
=============

Start by going through `the documentation`_ (generated from `/docs </docs/index.rst>`_).  If you need more help see below.

.. _the documentation: https://docs.openedx.org/projects/completion

License
*******

The code in this repository is licensed under version 3 of the AGPL unless
otherwise noted.

Please see `LICENSE <LICENSE>`_ for details.

Contributing
************

Contributions are very welcome.
Please read `How To Contribute <https://openedx.org/r/how-to-contribute>`_ for details.

This project is currently accepting all types of contributions, bug fixes,
security fixes, maintenance work, or new features.  However, please make sure
to have a discussion about your new feature idea with the maintainers prior to
beginning development to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing
your idea.

The Open edX Code of Conduct
****************************

All community members are expected to follow the `Open edX Code of Conduct`_.

.. _Open edX Code of Conduct: https://openedx.org/code-of-conduct/

People
******

The assigned maintainers for this component and other project details may be
found in `Backstage`_. Backstage pulls this data from the ``catalog-info.yaml``
file in this repo.

.. _Backstage: https://backstage.openedx.org/catalog/default/component/completion

Reporting Security Issues
*************************

Please do not report security issues in public. Please email security@openedx.org.

.. |pypi-badge| image:: https://img.shields.io/pypi/v/edx-completion.svg
    :target: https://pypi.python.org/pypi/edx-completion/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/openedx/completion/actions/workflows/ci.yml/badge.svg?branch=master
    :target: https://github.com/openedx/completion/actions/workflows/ci.yml?branch=master
    :alt: CI

.. |codecov-badge| image:: http://codecov.io/github/edx/completion/coverage.svg?branch=master
    :target: http://codecov.io/github/edx/completion?branch=master
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/completion/badge/?version=latest
    :target: https://docs.openedx.org/projects/completion
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/edx-completion.svg
    :target: https://pypi.python.org/pypi/edx-completion/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/edx/completion.svg
    :target: https://github.com/openedx/completion/blob/master/LICENSE.txt
    :alt: License

.. .. |status-badge| image:: https://img.shields.io/badge/Status-Experimental-yellow
.. |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Deprecated-orange
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Unsupported-red
