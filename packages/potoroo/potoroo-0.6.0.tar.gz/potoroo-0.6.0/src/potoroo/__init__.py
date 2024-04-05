"""Python implementations of the Repository and UnitOfWork abstractions."""

import logging as _logging

from ._repo import BasicRepo, QueryRepo, Repo
from ._uow import UnitOfWork


__all__ = ["BasicRepo", "Repo", "QueryRepo", "UnitOfWork"]

__author__ = "Bryan M Bugyi"
__email__ = "bryanbugyi34@gmail.com"
__version__ = "0.6.0"

_logging.getLogger(__name__).addHandler(_logging.NullHandler())
