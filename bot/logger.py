"""
Logging setup for the Uzbek TTS Telegram Bot.
Provides structured, async-safe logging with contextual information.
"""

import logging
import sys
from typing import Any, Dict


class ContextFilter(logging.Filter):
    """Add contextual information to log records."""
    
    def __init__(self):
        super().__init__()
        self.context: Dict[str, Any] = {}
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to the log record."""
        for key, value in self.context.items():
            setattr(record, key, value)
        return True
    
    def set_context(self, **kwargs: Any) -> None:
        """Set context for future log messages."""
        self.context.update(kwargs)
    
    def clear_context(self) -> None:
        """Clear all context."""
        self.context.clear()


# Global context filter
_context_filter = ContextFilter()


def setup_logging(level: str = "INFO") -> None:
    """
    Set up logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(_context_filter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))
    root_logger.addHandler(console_handler)
    
    # Reduce noise from aiogram
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_log_context(**kwargs: Any) -> None:
    """
    Set contextual information for logs.
    
    Args:
        **kwargs: Key-value pairs to add to log context
    """
    _context_filter.set_context(**kwargs)


def clear_log_context() -> None:
    """Clear all log context."""
    _context_filter.clear_context()
