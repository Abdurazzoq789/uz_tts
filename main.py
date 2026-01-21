"""
Uzbek TTS Telegram Bot - Main Entry Point

This bot monitors Telegram channels for messages containing #audio,
converts the text to speech using Google Cloud TTS (Uzbek language),
and posts the audio back to the channel.
"""

import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import get_config
from bot.logger import setup_logging, get_logger
from bot.handlers import router as handlers_router
from bot.commands import router as commands_router
from bot.admin_commands import router as admin_router
from bot.subscription_commands import router as subscription_router
from bot.payment_handlers import router as payment_router
from bot.middleware import ErrorHandlerMiddleware
from bot.client_middleware import BlacklistMiddleware, RegistrationMiddleware
from bot.subscription_middleware import SubscriptionMiddleware
from bot.exceptions import ConfigurationError
from database import init_database, close_database


async def main():
    """Main bot entry point."""
    # Load configuration
    try:
        config = get_config()
    except Exception as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Setup logging
    setup_logging(config.log_level)
    logger = get_logger(__name__)
    
    logger.info("=" * 60)
    logger.info("Uzbek TTS Telegram Bot Starting")
    logger.info("TTS Engine: Facebook MMS VITS (Open Source)")
    logger.info("=" * 60)
    logger.info(f"Trigger hashtag: {config.trigger_hashtag}")
    logger.info(f"Max text length: {config.max_text_length}")
    logger.info("=" * 60)
    
    # Initialize bot
    try:
        bot = Bot(
            token=config.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        # Get bot info
        bot_info = await bot.get_me()
        logger.info(f"Bot initialized: @{bot_info.username} ({bot_info.full_name})")
        
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}", exc_info=True)
        sys.exit(1)
    
    # Initialize database
    try:
        logger.info("Initializing database...")
        await init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        logger.warning("Bot will continue without database (limited functionality)")
    
    # Initialize dispatcher
    dp = Dispatcher()
    
    # Register middleware (order matters!)
    # 1. Registration - track all users/chats
    dp.message.middleware(RegistrationMiddleware())
    dp.channel_post.middleware(RegistrationMiddleware())
    
    # 2. Blacklist - enforce status checks
    dp.message.middleware(BlacklistMiddleware())
    dp.channel_post.middleware(BlacklistMiddleware())
    
    # 3. Subscription - enforce usage limits
    dp.message.middleware(SubscriptionMiddleware())
    dp.channel_post.middleware(SubscriptionMiddleware())
    
    # 4. Error handling - catch any errors
    dp.message.middleware(ErrorHandlerMiddleware())
    dp.channel_post.middleware(ErrorHandlerMiddleware())
    dp.callback_query.middleware(ErrorHandlerMiddleware())
    
    # Register routers (order matters: commands first, then handlers)
    dp.include_router(commands_router)  # /start, /help, callbacks
    dp.include_router(subscription_router)  # /subscription, payment callbacks
    dp.include_router(payment_router)  # payment processing (Stars + manual)
    dp.include_router(admin_router)  # admin commands
    dp.include_router(handlers_router)  # channel posts, private messages
    
    logger.info("Handlers and middleware registered")
    
    # Start polling
    try:
        logger.info("Starting bot polling...")
        await dp.start_polling(
            bot, 
            allowed_updates=["message", "channel_post", "callback_query"]
        )
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}", exc_info=True)
    finally:
        # Cleanup
        await close_database()
        await bot.session.close()
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
