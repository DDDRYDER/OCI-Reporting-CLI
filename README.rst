Reporting CLI for Oracle Cloud Infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

=====
About
=====

Provides a CLI to report resources deployed to an OCI Compartment.


============
Installation
============

Python 3.6.3+ are supported.

Requires the Python packages
::

    pip install configureparser, requests


Requires the Python SDK for Oracle Cloud Infrastructure
::

    pip install oci

See `Python SDK for Oracle Cloud Infrastructure`__ for additional information

__ https://github.com/oracle/oci-python-sdk

============
Development
============



========
Examples
========

::

  python cli.py oci_config1.txt compute
  python cli.py oci_config1.txt storage
  python cli.py oci_config1.txt database
  python cli.py oci_config1.txt shapes
  python cli.py oci_config1.txt images

=============
Documentation
=============


====
Help
====

Project is maintained by David Ryder - David.Ryder@oracle.com, DavidRyder@yahoo.com


=======
Changes
=======

See `CHANGELOG`__.

__ https://github.com/DDDRYDER/OCI-Reporting-CLI/blob/master/CHANGELOG.rst

============
Contributing
============



============
Known Issues
============



=======
License
=======

Copyright (c) 2016, 2018, Oracle and/or its affiliates. All rights reserved.

This CLI is dual licensed under the Universal Permissive License 1.0 and the Apache License 2.0.

See `LICENSE`__ for more details.

__ https://github.com/DDDRYDER/OCI-Reporting-CLI/blob/master/LICENSE.txt
