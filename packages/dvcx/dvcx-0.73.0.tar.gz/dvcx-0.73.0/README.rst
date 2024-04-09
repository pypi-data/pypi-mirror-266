|PyPI| |Status| |Python Version| |License|

|Tests| |Codecov| |pre-commit| |Black|

.. |PyPI| image:: https://img.shields.io/pypi/v/dvcx.svg
   :target: https://pypi.org/project/dvcx/
   :alt: PyPI
.. |Status| image:: https://img.shields.io/pypi/status/dvcx.svg
   :target: https://pypi.org/project/dvcx/
   :alt: Status
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/dvcx
   :target: https://pypi.org/project/dvcx
   :alt: Python Version
.. |License| image:: https://img.shields.io/pypi/l/dvcx
   :target: https://opensource.org/licenses/Apache-2.0
   :alt: License
.. |Tests| image:: https://github.com/iterative/dvcx/workflows/Tests/badge.svg
   :target: https://github.com/iterative/dvcx/actions?workflow=Tests
   :alt: Tests
.. |Codecov| image:: https://codecov.io/gh/iterative/dvcx/branch/main/graph/badge.svg?token=VSCP2T9R5X
   :target: https://app.codecov.io/gh/iterative/dvcx
   :alt: Codecov
.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Black


What is DVCx?
-------------

DVCx is a Python data manipulation library designed to work with unstructured AI datasets.
It provides a dataframe-like interface which can automatically reference data stored as files
(text, images, video) locally or in the cloud.

Why use DVCx?
-------------

1. **Storage as a single source of truth.** DVCx can organize unstructured data from storages
   and datalakes (local files, S3, GCS, Azure ADLS) into overlapping datasets without
   unnecessary file copies.
2. **Compute**. DVCx supports local parallelization and external compute workers for efficient
   data processing and AI metadata creation.
3. **Large scale.** In contrast to in-memory frameworks (like Pandas data frame), DVCx can work
   with datasets of millions and billions of records by using out-of-memory algorithms.
4. **Persistence and versioning**. Your datasets, your computed metadata, and paid API call
   results remain versioned and reusable.


Installation
------------

You can install *DVCx* via pip_ from PyPI_:

.. code:: console

   $ pip install dvcx


Usage
-----
DVCx can be used as a CLI (from system terminal), or as a Python library.

TODO: CLI usage

To use it from Python code, import class ``dvcx.catalog.Catalog``, which provides methods for all the same commands above, like ``ls()``, ``get()``, ``find()``, ``du()`` and ``index()``.

.. code:: py

    from dvcx.catalog import Catalog
    catalog = Catalog()
    catalog.ls(["gcs://dvcx-datalakes/dogs-and-cats/"], update=True)


How it’s related to DVC?
------------------------

`DVC <https://github.com/iterative/dvc/>`_ is an ML framework that helps connecting
unstructured data to ML models through pipelines to ensure reproducibility. DVCX,
created by DVC team, designed to handle the data preparation phase, thus functioning
upstream from DVC in the data management process.

Contributing
------------

Contributions are very welcome.
To learn more, see the `Contributor Guide`_.


License
-------

Distributed under the terms of the `Apache 2.0 license`_,
*DVCx* is free and open source software.


Issues
------

If you encounter any problems,
please `file an issue`_ along with a detailed description.


.. _Apache 2.0 license: https://opensource.org/licenses/Apache-2.0
.. _PyPI: https://pypi.org/
.. _file an issue: https://github.com/iterative/dvcx/issues
.. _pip: https://pip.pypa.io/
.. github-only
.. _Contributor Guide: CONTRIBUTING.rst
