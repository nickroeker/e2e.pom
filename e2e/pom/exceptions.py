"""Exceptions raised by `e2e.pom` at runtime."""


class PomError(Exception):
    """Base exception from which all `e2e.pom` errors inherit."""


class ElementNotUniqueErrror(PomError):
    """Raised when multiple DOM matches are found for a "unique" model."""


class ElementNotFoundErrror(PomError):
    """Raised when no DOM matches are found for a "unique" model."""
