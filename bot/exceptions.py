"""
Custom exceptions for the Uzbek TTS Telegram Bot.
"""


class BotException(Exception):
    """Base exception for all bot errors."""
    pass


class TTSError(BotException):
    """Raised when TTS generation fails."""
    pass


class TextProcessingError(BotException):
    """Raised when text processing fails."""
    pass


class ConfigurationError(BotException):
    """Raised when configuration is invalid or missing."""
    pass
