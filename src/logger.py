"""
Centralized logging utility for EHMS MyClub API pipeline.
Supports silent mode via SILENT_MODE environment variable.
"""
import os
import sys


class Logger:
    """
    Logger class that respects SILENT_MODE environment variable.
    When SILENT_MODE is set to 'true', '1', or 'yes', all output is suppressed.
    """

    def __init__(self):
        silent_mode = os.getenv('SILENT_MODE', '').lower()
        self.silent = silent_mode in ('true', '1', 'yes')

    def log(self, *args, **kwargs):
        """Print-like function that respects silent mode."""
        if not self.silent:
            print(*args, **kwargs)

    def error(self, *args, **kwargs):
        """Error logging that always outputs to stderr, even in silent mode."""
        print(*args, file=sys.stderr, **kwargs)


# Global logger instance
_logger = Logger()


def log(*args, **kwargs):
    """
    Logging function that respects SILENT_MODE environment variable.

    Usage:
        from src.logger import log
        log("This will only print if SILENT_MODE is not enabled")

    Environment Variables:
        SILENT_MODE: Set to 'true', '1', or 'yes' to suppress output
    """
    _logger.log(*args, **kwargs)


def error(*args, **kwargs):
    """
    Error logging function that always outputs to stderr.
    Errors are logged even in silent mode.

    Usage:
        from src.logger import error
        error("This error will always be printed")
    """
    _logger.error(*args, **kwargs)
