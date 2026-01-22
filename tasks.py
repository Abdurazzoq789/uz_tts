"""
Celery tasks for async TTS processing.
"""

import asyncio
from typing import Optional
from datetime import datetime

from celery import Task
from celery_config import celery_app
from bot.logger import setup_logging, get_logger
from bot.tts_engine import get_tts_engine
from bot.config import get_config
from aiogram import Bot
from aiogram.types import BufferedInputFile
from database import get_session
from database.repository import UsageStatsRepository
from database.models import TTSHistory
from sqlalchemy import select, update

# Setup logging for Celery worker
setup_logging(get_config().log_level)
logger = get_logger(__name__)


class DatabaseTask(Task):
    """Base task with database session support."""
    
    _session_maker = None
    
    @property
    def session_maker(self):
        """Get or create session maker."""
        if self._session_maker is None:
            from database import get_session_maker
            self._session_maker = get_session_maker()
        return self._session_maker


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name='tasks.process_tts_task',
    max_retries=3,
    default_retry_delay=60
)
def process_tts_task(
    self,
    tts_history_id: int,
    text: str,
    user_id: int,
    chat_id: int,
    bot_token: str
) -> dict:
    """
    Process TTS in background queue.
    
    Args:
        tts_history_id: ID of TTS history record
        text: Text to convert to speech
        user_id: User ID who requested TTS
        chat_id: Chat ID where to send audio
        bot_token: Bot token for sending message
    
    Returns:
        Dict with status and result
    """
    logger.info(f"Processing TTS task {tts_history_id} for user {user_id}")
    
    from database.sync_db import update_tts_status_sync, complete_tts_task_sync
    
    try:
        # Update status to processing (sync!)
        update_tts_status_sync(tts_history_id, 'processing')
        
        # Generate TTS audio (async operation)
        logger.info(f"Generating TTS for {len(text)} characters")
        tts_engine = get_tts_engine()
        
        # Run TTS in async context
        async def generate_audio():
            return await tts_engine.text_to_speech(text)
        
        audio_bytes = asyncio.run(generate_audio())
        logger.info(f"Generated audio: {len(audio_bytes)} bytes")
        
        # Send audio to chat (async operation)
        async def send_audio_to_chat():
            bot = Bot(token=bot_token)
            try:
                # Get bot info
                bot_info = await bot.get_me()
                bot_username = f"@{bot_info.username}" if bot_info.username else bot_info.full_name
                
                # Send voice message
                audio_file = BufferedInputFile(
                    audio_bytes,
                    filename="tts_audio.mp3"
                )
                
                await bot.send_voice(
                    chat_id=chat_id,
                    voice=audio_file,
                    caption=f"🎙️"
                )
                
                logger.info(f"Sent audio to chat {chat_id}")
            finally:
                await bot.session.close()
        
        asyncio.run(send_audio_to_chat())
        
        # Update completion status (sync!)
        complete_tts_task_sync(
            tts_history_id=tts_history_id,
            user_id=user_id,
            chat_id=chat_id,
            audio_duration=len(audio_bytes) // 16000,
            character_count=len(text)
        )
        
        logger.info(f"TTS task {tts_history_id} completed successfully")
        
        return {
            "status": "completed",
            "audio_size": len(audio_bytes),
            "text_length": len(text)
        }
        
    except Exception as e:
        logger.error(f"TTS task {tts_history_id} failed: {e}", exc_info=True)
        
        # Update status to failed (sync!)
        update_tts_status_sync(tts_history_id, 'failed', str(e))
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
