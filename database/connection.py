"""
Database connection and session management.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker
)

from .models import Base
from bot.config import get_config
from bot.logger import get_logger

logger = get_logger(__name__)

# Global engine and session maker
_engine: AsyncEngine | None = None
_async_session_maker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Get or create the database engine."""
    global _engine
    
    if _engine is None:
        config = get_config()
        
        _engine = create_async_engine(
            config.database_url,
            echo=config.database_echo,
            pool_size=config.database_pool_size,
            max_overflow=config.database_max_overflow,
            pool_pre_ping=True,  # Verify connections before using
        )
        
        logger.info(f"Database engine created: {config.database_url.split('@')[1]}")
    
    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """Get or create the session maker."""
    global _async_session_maker
    
    if _async_session_maker is None:
        engine = get_engine()
        _async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info("Database session maker created")
    
    return _async_session_maker


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session.
    
    Usage:
        async with get_session() as session:
            result = await session.execute(query)
    """
    session_maker = get_session_maker()
    session = session_maker()
    
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def init_database():
    """Initialize database tables."""
    engine = get_engine()
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created")


async def close_database():
    """Close database connections."""
    global _engine
    
    if _engine:
        await _engine.dispose()
        _engine = None
        logger.info("Database connections closed")
