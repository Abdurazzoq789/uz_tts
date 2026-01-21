"""
Audio sending utilities.
Handles sending voice messages to Telegram.
"""

import asyncio
from io import BytesIO
from aiogram import Bot
from aiogram.types import BufferedInputFile
from .logger import get_logger

logger = get_logger(__name__)


async def send_audio(
    bot: Bot,
    chat_id: int,
    audio_bytes: bytes,
    reply_to_message_id: int = None
):
    """
    Send audio as a voice message.
    
    Args:
        bot: Bot instance
        chat_id: Chat ID to send to
        audio_bytes: Audio data in MP3 format
        reply_to_message_id: Message ID to reply to (optional)
    """
    try:
        # Get bot info for username
        bot_info = await bot.get_me()
        bot_username = f"@{bot_info.username}" if bot_info.username else bot_info.full_name
        
        # Create input file from bytes
        audio_file = BufferedInputFile(
            audio_bytes,
            filename="tts_audio.mp3"
        )
        
        # Send as voice message
        message = await bot.send_voice(
            chat_id=chat_id,
            voice=audio_file,
            reply_to_message_id=reply_to_message_id,
            caption=f"🎙️ {bot_username}"
        )
        
        logger.info(f"Sent audio to chat {chat_id}, size: {len(audio_bytes)} bytes")
        
        return message
    except Exception as e:
        logger.error(f"Failed to send audio: {e}", exc_info=True)
        raise


async def send_multiple_audios(
    bot: Bot,
    chat_id: int,
    audio_chunks: list[bytes],
    reply_to_message_id: int,
    delay_seconds: float = 1.0
) -> None:
    """
    Send multiple audio chunks with delays between them.
    
    Args:
        bot: Telegram bot instance
        chat_id: Channel chat ID
        audio_chunks: List of audio bytes
        reply_to_message_id: Message ID to reply to
        delay_seconds: Delay between sending chunks
    """
    logger.info(f"Sending {len(audio_chunks)} audio chunks")
    
    for i, audio_bytes in enumerate(audio_chunks, 1):
        try:
            await send_audio(bot, chat_id, audio_bytes, reply_to_message_id)
            
            # Add delay between chunks (except after last one)
            if i < len(audio_chunks):
                logger.debug(f"Waiting {delay_seconds}s before next chunk")
                await asyncio.sleep(delay_seconds)
                
        except Exception as e:
            logger.error(f"Failed to send audio chunk {i}/{len(audio_chunks)}: {e}")
            # Continue sending remaining chunks even if one fails
            continue
    
    logger.info(f"Completed sending {len(audio_chunks)} audio chunks")
