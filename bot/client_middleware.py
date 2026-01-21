"""
Blacklist and status enforcement middleware.
Checks user and chat status before processing messages.
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from services.client_service import ClientService
from bot.logger import get_logger

logger = get_logger(__name__)


class BlacklistMiddleware(BaseMiddleware):
    """
    Middleware to enforce blacklist and status checks.
    Blocks messages from blacklisted or inactive users/chats.
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Check user and chat status before processing.
        
        Args:
            handler: Next handler in chain
            event: Telegram event (Message, CallbackQuery, etc.)
            data: Handler data
        
        Returns:
            Handler result or None if blocked
        """
        # Only process messages and callback queries
        if not isinstance(event, Message):
            return await handler(event, data)
        
        message: Message = event
        
        # Check user status
        if message.from_user:
            user_check = await ClientService.check_user_status(message.from_user.id)
            
            if not user_check["allowed"]:
                logger.warning(
                    f"Blocked message from user {message.from_user.id}: {user_check['reason']}"
                )
                
                # Send error message only for private chats
                if message.chat.type == "private":
                    await message.answer(
                        f"⛔ {user_check['reason']}\n\n"
                        "If you believe this is an error, please contact support."
                    )
                
                return  # Block further processing
        
        # Check chat status (for channels and groups)
        if message.chat.type in ["group", "supergroup", "channel"]:
            chat_check = await ClientService.check_chat_status(message.chat.id)
            
            if not chat_check["allowed"]:
                logger.warning(
                    f"Blocked message from chat {message.chat.id}: {chat_check['reason']}"
                )
                return  # Block further processing (no message sent to avoid spam)
        
        # All checks passed - continue processing
        return await handler(event, data)


class RegistrationMiddleware(BaseMiddleware):
    """
    Middleware to auto-register users and chats.
    Ensures all interactions are tracked in the database.
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Auto-register user and chat on every interaction.
        
        Args:
            handler: Next handler in chain
            event: Telegram event
            data: Handler data
        
        Returns:
            Handler result
        """
        if not isinstance(event, Message):
            return await handler(event, data)
        
        message: Message = event
        
        # Register user
        if message.from_user and not message.from_user.is_bot:
            try:
                user = await ClientService.register_user(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                    language_code=message.from_user.language_code
                )
                
                # Store user in handler data for later use
                data['db_user'] = user
                
            except Exception as e:
                logger.error(f"Failed to register user {message.from_user.id}: {e}")
        
        # Register chat
        try:
            chat = await ClientService.register_chat(
                chat_id=message.chat.id,
                chat_type=message.chat.type,
                title=message.chat.title,
                username=message.chat.username,
                created_by_user_id=message.from_user.id if message.from_user else None
            )
            
            # Store chat in handler data
            data['db_chat'] = chat
            
        except Exception as e:
            logger.error(f"Failed to register chat {message.chat.id}: {e}")
        
        # Continue processing
        return await handler(event, data)
