Changelog
=========

All notable changes to this project will be documented in this file.


The format is based on `Keep a Changelog`_,
and this project adheres to `Semantic Versioning`_.


Version 0.0.0-dev6 (2024-04-05)
-------------------------------

* Added: full uppercase `Databricks` profiles e.g. `DEFAULT` are now supported.

Version 0.0.0-dev5 (2024-03-12)
-------------------------------

* Changed: `core.AzureBlobConnector.list_blobs_in_directory()`
  now returns absolute paths instead of blobs basenames
  and do not include parent directory


Version 0.0.0-dev4 (2024-03-12)
-------------------------------

* Added: Method to list blobs under a specific path in a container


Version 0.0.0-dev3 (2023-10-12)
-------------------------------

* Changed: Authentication to AAD resources
* Changed: Documentation and Metadata


Version 0.0.0-dev2 (2023-10-09)
-------------------------------

* Added: Description on PyPI
* Changed: Documentation


Version 0.0.0-dev1 (2023-10-09)
-------------------------------

* Added: Initial public pre-release


Version 0.0.0-dev0 (2023-10-06)
-------------------------------

* Added: Initial pre-release


.. _Keep a Changelog:
    https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning:
    https://semver.org/spec/v2.0.0.html
