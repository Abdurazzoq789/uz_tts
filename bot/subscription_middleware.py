"""
Subscription enforcement middleware.
Checks usage limits and subscription status before allowing TTS.
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from services.subscription_service import SubscriptionService
from bot.logger import get_logger

logger = get_logger(__name__)


class SubscriptionMiddleware(BaseMiddleware):
    """
    Middleware to enforce subscription and usage limits.
    Blocks TTS requests that exceed limits or require subscription.
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Check subscription and usage limits.
        
        Args:
            handler: Next handler in chain
            event: Telegram event
            data: Handler data
        
        Returns:
            Handler result or None if blocked
        """
        if not isinstance(event, Message):
            return await handler(event, data)
        
        message: Message = event
        
        # Only check for text messages (TTS requests)
        if not message.text:
            return await handler(event, data)
        
        # Skip checks for commands
        if message.text.startswith('/'):
            return await handler(event, data)
        
        # Check if this is a TTS request
        # For channels: must have #audio hashtag
        # For private: any text is TTS request
        from bot.config import get_config
        config = get_config()
        
        is_tts_request = False
        
        if message.chat.type in ['group', 'supergroup', 'channel']:
            # Channel/group - check for hashtag
            if config.trigger_hashtag.lower() in message.text.lower():
                is_tts_request = True
        elif message.chat.type == 'private':
            # Private chat - any text is TTS (unless it starts with /)
            is_tts_request = True
        
        if not is_tts_request:
            return await handler(event, data)
        
        # Skip subscription check for channel posts (no from_user)
        # Channels are handled separately - they need channel subscription
        if not message.from_user:
            logger.debug("Skipping subscription check for channel post")
            return await handler(event, data)
        
        # Check usage limit
        if message.from_user:
            limit_check = await SubscriptionService.check_usage_limit(
                user_id=message.from_user.id,
                chat_id=message.chat.id,
                chat_type=message.chat.type
            )
            
            if not limit_check["allowed"]:
                logger.warning(
                    f"Usage limit exceeded for user {message.from_user.id}: {limit_check['reason']}"
                )
                
                # Send upgrade message
                if message.chat.type == 'private':
                    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                    
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="💳 Upgrade to Unlimited",
                            callback_data="subscribe"
                        )],
                        [InlineKeyboardButton(
                            text="ℹ️ View Plans",
                            callback_data="view_plans"
                        )]
                    ])
                    
                    await message.answer(
                        f"⚠️ {limit_check['reason']}",
                        reply_markup=keyboard
                    )
                
                return  # Block further processing
            
            # Log remaining usage for free tier
            if limit_check["remaining"] > 0 and limit_check["tariff_name"] == "free_dm":
                logger.debug(
                    f"User {message.from_user.id} has {limit_check['remaining']} "
                    f"free TTS remaining this month"
                )
        
        # All checks passed - continue processing
        return await handler(event, data)
