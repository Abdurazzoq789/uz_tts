"""
Database repository for CRUD operations.
Provides high-level database access methods.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from decimal import Decimal

from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Chat, Tariff, Subscription, Payment, TTSHistory, UsageStats
from bot.logger import get_logger

logger = get_logger(__name__)


class UserRepository:
    """User database operations."""
    
    @staticmethod
    async def get_or_create(
        session: AsyncSession,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: Optional[str] = None
    ) -> User:
        """Get existing user or create new one."""
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            user = User(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                language_code=language_code,
                status='active'
            )
            session.add(user)
            await session.flush()
            logger.info(f"Created new user: {user_id}")
        else:
            # Update user info if changed
            if username and user.username != username:
                user.username = username
            if first_name and user.first_name != first_name:
                user.first_name = first_name
                
        return user
    
    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_status(session: AsyncSession, user_id: int, status: str):
        """Update user status."""
        await session.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(status=status, updated_at=datetime.now())
        )


class ChatRepository:
    """Chat database operations."""
    
    @staticmethod
    async def get_or_create(
        session: AsyncSession,
        chat_id: int,
        chat_type: str,
        title: Optional[str] = None,
        username: Optional[str] = None,
        created_by_user_id: Optional[int] = None
    ) -> Chat:
        """Get existing chat or create new one."""
        result = await session.execute(
            select(Chat).where(Chat.chat_id == chat_id)
        )
        chat = result.scalar_one_or_none()
        
        if chat is None:
            chat = Chat(
                chat_id=chat_id,
                chat_type=chat_type,
                title=title,
                username=username,
                created_by_user_id=created_by_user_id,
                status='active'
            )
            session.add(chat)
            await session.flush()
            logger.info(f"Created new chat: {chat_id} ({chat_type})")
                
        return chat


class TariffRepository:
    """Tariff database operations."""
    
    @staticmethod
    async def get_all_visible(session: AsyncSession) -> List[Tariff]:
        """Get all visible tariffs."""
        result = await session.execute(
            select(Tariff).where(Tariff.is_visible == True)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_by_name(session: AsyncSession, name: str) -> Optional[Tariff]:
        """Get tariff by name."""
        result = await session.execute(
            select(Tariff).where(Tariff.name == name)
        )
        return result.scalar_on_or_none()


class SubscriptionRepository:
    """Subscription database operations."""
    
    @staticmethod
    async def get_active(
        session: AsyncSession,
        user_id: Optional[int] = None,
        chat_id: Optional[int] = None
    ) -> Optional[Subscription]:
        """Get active subscription for user or chat."""
        conditions = [
            Subscription.is_active == True,
            Subscription.end_date > datetime.now()
        ]
        
        if user_id:
            conditions.append(Subscription.user_id == user_id)
        if chat_id:
            conditions.append(Subscription.chat_id == chat_id)
            
        result = await session.execute(
            select(Subscription).where(and_(*conditions))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(
        session: AsyncSession,
        user_id: Optional[int],
        chat_id: Optional[int],
        tariff_id: int,
        duration_months: int = 1
    ) -> Subscription:
        """Create new subscription."""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30 * duration_months)
        
        subscription = Subscription(
            user_id=user_id,
            chat_id=chat_id,
            tariff_id=tariff_id,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
        session.add(subscription)
        await session.flush()
        
        logger.info(f"Created subscription for user={user_id} chat={chat_id} tariff={tariff_id}")
        return subscription


class UsageStatsRepository:
    """Usage stats database operations."""
    
    @staticmethod
    async def get_monthly_usage(
        session: AsyncSession,
        user_id: int,
        chat_id: Optional[int] = None
    ) -> UsageStats:
        """Get or create current month usage."""
        now = datetime.now()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get next month for period_end
        if now.month == 12:
            period_end = period_start.replace(year=now.year + 1, month=1)
        else:
            period_end = period_start.replace(month=now.month + 1)
        
        result = await session.execute(
            select(UsageStats).where(
                and_(
                    UsageStats.user_id == user_id,
                    UsageStats.chat_id == chat_id,
                    UsageStats.period_start == period_start.date()
                )
            )
        )
        stats = result.scalar_one_or_none()
        
        if stats is None:
            stats = UsageStats(
                user_id=user_id,
                chat_id=chat_id,
                period_start=period_start.date(),
                period_end=period_end.date(),
                tts_count=0,
                total_characters=0
            )
            session.add(stats)
            await session.flush()
            
        return stats
    
    @staticmethod
    async def increment_usage(
        session: AsyncSession,
        user_id: int,
        chat_id: Optional[int],
        character_count: int
    ):
        """Increment usage stats."""
        stats = await UsageStatsRepository.get_monthly_usage(session, user_id, chat_id)
        stats.tts_count += 1
        stats.total_characters += character_count
