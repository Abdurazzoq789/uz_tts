"""
Synchronous database operations for Celery tasks.
Celery workers can't share async event loops, so we use sync operations.
"""

from sqlalchemy import create_engine, update, select
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

from bot.config import get_config
from database.models import TTSHistory, UsageStats

# Create synchronous engine (no asyncio issues!)
config = get_config()
# Convert async URL to sync: postgresql+asyncpg -> postgresql+psycopg2
sync_url = config.database_url.replace('postgresql+asyncpg', 'postgresql+psycopg2')

sync_engine = create_engine(
    sync_url,
    echo=config.database_echo,
    pool_pre_ping=True,
    pool_recycle=3600
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    expire_on_commit=False
)


@contextmanager
def get_sync_session() -> Session:
    """Get a synchronous database session for Celery tasks."""
    session = SyncSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def update_tts_status_sync(
    tts_history_id: int,
    status: str,
    error_message: Optional[str] = None
):
    """Update TTS history status synchronously."""
    with get_sync_session() as session:
        values = {"status": status}
        
        if error_message:
            values["error_message"] = error_message
        
        if status == 'completed':
            values["completed_at"] = datetime.now()
        
        session.execute(
            update(TTSHistory)
            .where(TTSHistory.id == tts_history_id)
            .values(**values)
        )


def complete_tts_task_sync(
    tts_history_id: int,
    user_id: Optional[int],  # None for channel posts
    chat_id: int,
    audio_duration: int,
    character_count: int
):
    """Mark TTS as completed and update usage stats synchronously."""
    with get_sync_session() as session:
        # Update TTS history
        session.execute(
            update(TTSHistory)
            .where(TTSHistory.id == tts_history_id)
            .values(
                status='completed',
                completed_at=datetime.now(),
                audio_duration=audio_duration
            )
        )
        
        # Update usage stats only if user_id is present (skip for channel posts)
        if user_id is not None:
            # Get current month start
            now = datetime.now()
            period_start = datetime(now.year, now.month, 1)
            
            # Try to get existing usage stats
            result = session.execute(
                select(UsageStats)
                .where(
                    UsageStats.user_id == user_id,
                    UsageStats.chat_id == chat_id,
                    UsageStats.period_start == period_start
                )
            )
            usage = result.scalar_one_or_none()
            
            if usage:
                # Update existing
                usage.tts_count += 1
                usage.total_characters += character_count
            else:
                # Create new
                usage = UsageStats(
                    user_id=user_id,
                    chat_id=chat_id,
                    period_start=period_start,
                    tts_count=1,
                    total_characters=character_count
                )
                session.add(usage)
