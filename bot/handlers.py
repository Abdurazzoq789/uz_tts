"""
Message handlers for the Uzbek TTS Telegram Bot.
Handles channel posts with #audio hashtag.
"""

from aiogram import Router, F
from aiogram.types import Message
from .config import get_config
from .text_processor import process_text
from .text_splitter import split_text
from .tts_engine import get_tts_engine
from .audio_sender import send_audio, send_multiple_audios
from .cache import get_audio_cache
from .logger import get_logger

logger = get_logger(__name__)

# Create router for handlers
router = Router()


@router.channel_post(F.text)
async def handle_channel_post(message: Message):
    """
    Handle channel posts with text content.
    Checks for #audio hashtag and processes TTS if present.
    
    Args:
        message: Channel post message
    """
    # Ignore messages from bots
    if message.from_user and message.from_user.is_bot:
        logger.debug("Ignoring message from bot")
        return
    
    # Get configuration
    config = get_config()
    
    # Check if message contains trigger hashtag
    if not message.text or config.trigger_hashtag.lower() not in message.text.lower():
        logger.debug(f"Message doesn't contain {config.trigger_hashtag}, ignoring")
        return
    
    logger.info(
        f"Processing message {message.message_id} from channel {message.chat.id}, "
        f"original text length: {len(message.text)}"
    )
    
    # Process text (remove hashtag, validate)
    processed_text = process_text(message.text, config.trigger_hashtag)
    
    if not processed_text:
        logger.warning("Text is empty after processing, skipping")
        return
    
    # Queue TTS request (moved to async background processing)
    try:
        from services.tts_service import TTSService
        
        tts_record = await TTSService.queue_tts_request(
            user_id=message.from_user.id if message.from_user else None,  # None for channel posts
            chat_id=message.chat.id,
            original_text=message.text,
            processed_text=processed_text
        )
        
        logger.info(
            f"Queued TTS request {tts_record.id} for channel {message.chat.id}. "
            "Audio will be generated and sent asynchronously."
        )
        
    except Exception as e:
        logger.error(
            f"Failed to queue TTS for message {message.message_id}: {e}",
            exc_info=True
        )


@router.message(F.text & (F.chat.type == "private"))
async def handle_private_message(message: Message):
    """
    Handle text messages in private chat.
    Converts text to speech without requiring #audio hashtag.
    
    Args:
        message: Private message from user
    """
    # Get text
    text = message.text.strip()
    
    # Skip commands (they're handled by command router)
    if text.startswith('/'):
        logger.debug(f"Skipping command in private chat: {text[:20]}")
        return
    
    # Skip empty messages
    if not text:
        logger.debug("Ignoring empty message")
        return
    
    logger.info(
        f"Processing private message from user {message.from_user.id}, "
        f"text length: {len(text)}"
    )
    
    # Get configuration
    config = get_config()
    
    # Process text directly (no hashtag removal needed in private chat)
    # Just validate it contains letters
    if not any(c.isalpha() for c in text):
        await message.answer(
            "⚠️ Please send text containing letters.\n"
            "Example: Salom dunyo!"
        )
        return
    
    # Queue TTS request (async processing)
    try:
        from services.tts_service import TTSService
        
        # Show typing indicator
        await message.bot.send_chat_action(message.chat.id, "record_voice")
        
        tts_record = await TTSService.queue_tts_request(
            user_id=message.from_user.id,
            chat_id=message.chat.id,
            original_text=text,
            processed_text=text  # No preprocessing for private messages
        )
        
        logger.info(
            f"Queued TTS request {tts_record.id} for user {message.from_user.id}. "
            "Audio will be generated and sent shortly."
        )
        
    except Exception as e:
        logger.error(
            f"Failed to queue TTS for user {message.from_user.id}: {e}",
            exc_info=True
        )
        await message.answer(
            "❌ Sorry, something went wrong processing your text.\n"
            "Please try again or contact support."
        )
