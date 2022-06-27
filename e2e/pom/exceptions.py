"""Exceptions raised by `e2e.pom` at runtime."""


class PomError(Exception):
    """Base exception from which all `e2e.pom` errors inherit."""


class ElementNotUniqueError(PomError):
    """Raised when multiple DOM matches are found for a "unique" model."""


class ElementNotFoundError(PomError):
    """Raised when no DOM matches are found for a "unique" model."""


class TimeoutError(PomError):
    """Raised when an element action times out due to some waited-upon condition."""
