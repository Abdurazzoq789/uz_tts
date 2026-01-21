"""
Subscription and billing service.
Handles subscription checks, usage limits, and billing logic.
"""

from typing import Optional, Dict
from datetime import datetime

from database import get_session
from database.repository import (
    UserRepository, SubscriptionRepository, 
    TariffRepository, UsageStatsRepository
)
from bot.config import get_config
from bot.logger import get_logger

logger = get_logger(__name__)


class SubscriptionService:
    """Service for managing subscriptions and usage limits."""
    
    @staticmethod
    async def check_usage_limit(user_id: int, chat_id: int, chat_type: str) -> Dict:
        """
        Check if user can use TTS based on tariff and usage.
        
        Args:
            user_id: User ID
            chat_id: Chat ID
            chat_type: Chat type (private, group, channel)
        
        Returns:
            Dict with:
                - allowed (bool): Whether user can use TTS
                - reason (str): Reason if not allowed
                - remaining (int): Remaining uses (-1 for unlimited)
                - upgrade_needed (bool): Whether upgrade is needed
                - tariff_name (str): Current tariff name
        """
        config = get_config()
        
        async with get_session() as session:
            # Get user
            user = await UserRepository.get_by_id(session, user_id)
            
            # Check for active subscription (user-level or chat-level)
            subscription = await SubscriptionRepository.get_active(
                session,
                user_id=user_id if chat_type == 'private' else None,
                chat_id=chat_id if chat_type != 'private' else None
            )
            
            if subscription:
                # Has active subscription - get tariff
                from sqlalchemy import select
                from database.models import Tariff
                result = await session.execute(
                    select(Tariff).where(Tariff.id == subscription.tariff_id)
                )
                tariff = result.scalar_one()
                
                # Check if subscription is expired
                if subscription.end_date < datetime.now():
                    logger.info(f"Subscription expired for user {user_id}")
                    return {
                        "allowed": False,
                        "reason": "Your subscription has expired. Please renew to continue.",
                        "remaining": 0,
                        "upgrade_needed": True,
                        "tariff_name": tariff.name
                    }
                
                # VIP or paid subscription - unlimited
                limits = tariff.limits or {}
                tts_limit = limits.get('tts_per_month', -1)
                
                if tts_limit == -1:  # Unlimited
                    return {
                        "allowed": True,
                        "reason": "",
                        "remaining": -1,
                        "upgrade_needed": False,
                        "tariff_name": tariff.name
                    }
            
            # No active subscription - check free tier
            if chat_type == 'private':
                # Get monthly usage
                usage = await UsageStatsRepository.get_monthly_usage(session, user_id, chat_id)
                
                if usage.tts_count >= config.free_tier_tts_limit:
                    logger.info(f"User {user_id} exceeded free tier limit")
                    return {
                        "allowed": False,
                        "reason": (
                            f"You've used all {config.free_tier_tts_limit} free TTS credits this month.\n"
                            f"Upgrade to unlimited for ${config.paid_monthly_price}/month!"
                        ),
                        "remaining": 0,
                        "upgrade_needed": True,
                        "tariff_name": "free_dm"
                    }
                
                # Within free tier
                remaining = config.free_tier_tts_limit - usage.tts_count
                return {
                    "allowed": True,
                    "reason": "",
                    "remaining": remaining,
                    "upgrade_needed": False,
                    "tariff_name": "free_dm"
                }
            
            else:  # Channel or group
                # Channels and groups require subscription
                logger.info(f"Channel/group {chat_id} requires subscription")
                return {
                    "allowed": False,
                    "reason": (
                        "Channels and groups require a subscription.\n"
                        f"Subscribe for ${config.paid_monthly_price}/month to use TTS here!"
                    ),
                    "remaining": 0,
                    "upgrade_needed": True,
                    "tariff_name": None
                }
    
    @staticmethod
    async def get_subscription_info(user_id: int) -> Optional[Dict]:
        """
        Get user's subscription information.
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with subscription info or None
        """
        async with get_session() as session:
            subscription = await SubscriptionRepository.get_active(session, user_id=user_id)
            
            if not subscription:
                return None
            
            from sqlalchemy import select
            from database.models import Tariff
            result = await session.execute(
                select(Tariff).where(Tariff.id == subscription.tariff_id)
            )
            tariff = result.scalar_one_or_none()
            
            if not tariff:
                return None
            
            return {
                "tariff_name": tariff.name,
                "tariff_description": tariff.description,
                "price": float(tariff.price),
                "currency": tariff.currency,
                "start_date": subscription.start_date,
                "end_date": subscription.end_date,
                "is_active": subscription.is_active,
                "days_remaining": (subscription.end_date - datetime.now()).days
            }
