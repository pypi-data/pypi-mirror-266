# on titanq package hover when imported, this will show as tooltip in most modern IDE (this comment won't)

"""
TitanQ
======

The TitanQ SDK for python. This package will let you use InfinityQ's QUBO solver named TitanQ


Documentation
-------------

* Documentation is avaiable as sphinx docstrings
* A Quickstart example will be soon available


License
-----------------------------

Apache Software License (Apache 2.0)

"""

# These symbols must be exposed by this lib
from ._model import Model, Vtype, errors, Target, OptimizeResponse

# S3Storage must be exposed to the end user if he wishes to use s3 buckets
from ._storage import S3Storage

# logger config
import logging as _logging
_logging.getLogger("TitanQ").addHandler(_logging.NullHandler())