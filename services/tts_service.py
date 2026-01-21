"""
TTS service for queueing and tracking TTS requests.
"""

from typing import Optional
from datetime import datetime

from database import get_session
from database.models import TTSHistory
from tasks import process_tts_task
from bot.logger import get_logger
from bot.config import get_config

logger = get_logger(__name__)


class TTSService:
    """Service for managing TTS requests through queue."""
    
    @staticmethod
    async def queue_tts_request(
        user_id: Optional[int],  # None for channel posts
        chat_id: int,
        original_text: str,
        processed_text: str
    ) -> TTSHistory:
        """
        Queue a TTS request for async processing.
        
        Args:
            user_id: User who requested TTS
            chat_id: Chat where audio should be sent
            original_text: Original message text
            processed_text: Processed text for TTS
        
        Returns:
            TTS history record
        """
        # Create TTS history record
        async with get_session() as session:
            tts_record = TTSHistory(
                user_id=user_id,
                chat_id=chat_id,
                original_text=original_text,
                processed_text=processed_text,
                status='pending'
            )
            session.add(tts_record)
            await session.flush()
            
            tts_id = tts_record.id
            await session.commit()
        
        logger.info(f"Created TTS request {tts_id} for user {user_id}")
        
        # Queue task
        config = get_config()
        task = process_tts_task.delay(
            tts_history_id=tts_id,
            text=processed_text,
            user_id=user_id,
            chat_id=chat_id,
            bot_token=config.bot_token
        )
        
        logger.info(f"Queued TTS task {task.id} for record {tts_id}")
        
        # Return updated record
        async with get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(TTSHistory).where(TTSHistory.id == tts_id)
            )
            return result.scalar_one()
    
    @staticmethod
    async def get_tts_status(tts_id: int) -> Optional[dict]:
        """
        Get status of TTS request.
        
        Args:
            tts_id: TTS history ID
        
        Returns:
            Dict with status info or None
        """
        async with get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(TTSHistory).where(TTSHistory.id == tts_id)
            )
            tts_record = result.scalar_one_or_none()
            
            if tts_record is None:
                return None
            
            return {
                "id": tts_record.id,
                "status": tts_record.status,
                "created_at": tts_record.created_at,
                "completed_at": tts_record.completed_at,
                "error_message": tts_record.error_message
            }
