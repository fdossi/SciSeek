"""Domain exceptions for SciSeek core."""


class SciSeekError(Exception):
    """Base exception for SciSeek."""


class ValidationError(SciSeekError):
    """Input validation error."""


class SearchSyntaxError(ValidationError):
    """Invalid search syntax."""


class ExportError(SciSeekError):
    """Export operation failed."""


class CacheError(SciSeekError):
    """Cache operation failed."""
