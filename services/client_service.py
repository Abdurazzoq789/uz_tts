"""
Client management services.
Handles user and chat registration, tracking, and status management.
"""

from typing import Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from database.models import User, Chat
from database.repository import UserRepository, ChatRepository, UsageStatsRepository
from bot.logger import get_logger

logger = get_logger(__name__)


class ClientService:
    """Service for managing bot clients (users and chats)."""
    
    @staticmethod
    async def register_user(
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: Optional[str] = None
    ) -> User:
        """
        Register or update user in database.
        Called on every user interaction to keep data fresh.
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            last_name: User's last name
            language_code: User's language code
        
        Returns:
            User object
        """
        async with get_session() as session:
            user = await UserRepository.get_or_create(
                session,
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                language_code=language_code
            )
            await session.commit()
            
        logger.debug(f"User registered/updated: {user_id} (@{username})")
        return user
    
    @staticmethod
    async def register_chat(
        chat_id: int,
        chat_type: str,
        title: Optional[str] = None,
        username: Optional[str] = None,
        created_by_user_id: Optional[int] = None
    ) -> Chat:
        """
        Register or update chat in database.
        
        Args:
            chat_id: Telegram chat ID
            chat_type: Type of chat (private, group, channel)
            title: Chat title
            username: Chat username
            created_by_user_id: User who triggered registration
        
        Returns:
            Chat object
        """
        async with get_session() as session:
            chat = await ChatRepository.get_or_create(
                session,
                chat_id=chat_id,
                chat_type=chat_type,
                title=title,
                username=username,
                created_by_user_id=created_by_user_id
            )
            await session.commit()
            
        logger.debug(f"Chat registered/updated: {chat_id} ({chat_type})")
        return chat
    
    @staticmethod
    async def check_user_status(user_id: int) -> dict:
        """
        Check if user is allowed to use the bot.
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            Dict with 'allowed' (bool) and 'reason' (str) keys
        """
        async with get_session() as session:
            user = await UserRepository.get_by_id(session, user_id)
            
            if user is None:
                # User not registered yet - allow (will be auto-registered)
                return {"allowed": True, "reason": ""}
            
            if user.status == 'blacklisted':
                logger.warning(f"Blacklisted user attempted access: {user_id}")
                return {
                    "allowed": False,
                    "reason": "You have been blocked from using this bot."
                }
            
            if user.status == 'inactive':
                logger.info(f"Inactive user attempted access: {user_id}")
                return {
                    "allowed": False,
                    "reason": "Your account is inactive. Please contact support."
                }
            
            return {"allowed": True, "reason": ""}
    
    @staticmethod
    async def check_chat_status(chat_id: int) -> dict:
        """
        Check if chat is allowed to use the bot.
        
        Args:
            chat_id: Telegram chat ID
        
        Returns:
            Dict with 'allowed' (bool) and 'reason' (str) keys
        """
        async with get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(Chat).where(Chat.chat_id == chat_id)
            )
            chat = result.scalar_one_or_none()
            
            if chat is None:
                # Chat not registered yet - allow (will be auto-registered)
                return {"allowed": True, "reason": ""}
            
            if chat.status == 'blacklisted':
                logger.warning(f"Blacklisted chat attempted access: {chat_id}")
                return {
                    "allowed": False,
                    "reason": "This chat has been blocked from using this bot."
                }
            
            if chat.status == 'inactive':
                return {
                    "allowed": False,
                    "reason": "This chat is inactive."
                }
            
            return {"allowed": True, "reason": ""}
    
    @staticmethod
    async def get_user_stats(user_id: int) -> dict:
        """
        Get user statistics.
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            Dict with usage statistics
        """
        async with get_session() as session:
            # Get current month usage
            usage = await UsageStatsRepository.get_monthly_usage(session, user_id)
            
            # Get user
            user = await UserRepository.get_by_id(session, user_id)
            
            return {
                "user_id": user_id,
                "status": user.status if user else "unknown",
                "monthly_tts_count": usage.tts_count,
                "monthly_characters": usage.total_characters,
                "created_at": user.created_at if user else None
            }
    
    @staticmethod
    async def update_user_status(user_id: int, status: str):
        """
        Update user status (admin operation).
        
        Args:
            user_id: Telegram user ID
            status: New status (active, inactive, blacklisted)
        """
        async with get_session() as session:
            await UserRepository.update_status(session, user_id, status)
            await session.commit()
            
        logger.info(f"Updated user {user_id} status to: {status}")
