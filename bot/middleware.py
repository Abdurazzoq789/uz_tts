"""
Error handling middleware for the bot.
"""

from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from .logger import get_logger

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseMiddleware):
    """Middleware to catch and log all errors."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        """Handle the update with error catching."""
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(
                f"Error handling update: {e}",
                exc_info=True,
                extra={"event_type": type(event).__name__}
            )
            # Don't re-raise to prevent bot crashes
            return None
