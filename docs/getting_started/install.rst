============
Installation
============

.. _install:

There are two common ways to install vstools.

The first is to install the latest release build through `pypi <https://pypi.org/project/vstools/>`_.

You can use pip to do this, as demonstrated below:


.. code-block:: console

    pip install vstools --no-cache-dir -U

This ensures that any previous versions will be overwritten and vstools will be upgraded if you had already previously installed it.

------------------

The second method is to build the latest version from git.

This will be less stable, but will feature the most up-to-date features, as well as accurately reflect the documentation.

.. code-block:: console

    pip install git+https://github.com/Setsugennoao/vs-tools.git -U

It's recommended you use a release version over building from git
unless you require new functionality only available upstream.
