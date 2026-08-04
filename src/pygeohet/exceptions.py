"""Project-specific exceptions for explicit statistical failure modes."""


class PyGeoHetError(Exception):
    """Base class for pyGeoHet errors."""


class InvalidDataError(PyGeoHetError, ValueError):
    """Raised when input arrays cannot define the requested statistic."""


class MissingDataError(InvalidDataError):
    """Raised when missing values are present under ``missing='raise'``."""


class ConstantResponseError(InvalidDataError):
    """Raised when the response has zero total sum of squares."""


class SmallStratumError(InvalidDataError):
    """Raised when one or more strata contain too few observations."""
