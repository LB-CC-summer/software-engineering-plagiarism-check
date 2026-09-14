"""Domain-specific errors raised by the plagiarism checker."""


class PlagiarismError(Exception):
    """Base class for expected, user-facing errors."""


class CommandLineError(PlagiarismError):
    """Raised when command-line arguments do not match the required format."""


class DocumentReadError(PlagiarismError):
    """Raised when an input document cannot be opened or read."""


class DocumentDecodeError(PlagiarismError):
    """Raised when an input document cannot be decoded as supported text."""


class AnswerWriteError(PlagiarismError):
    """Raised when the answer file cannot be written."""
