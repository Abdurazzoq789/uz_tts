"""
Payment service for handling subscriptions and payments.
"""

from typing import Optional
from datetime import datetime, timedelta
from decimal import Decimal

from database import get_session
from database.models import Payment, Subscription
from database.repository import SubscriptionRepository, TariffRepository
from bot.logger import get_logger

logger = get_logger(__name__)


class PaymentService:
    """Service for managing payments and subscriptions."""
    
    @staticmethod
    async def create_payment_record(
        user_id: int,
        tariff_id: int,
        amount: Decimal,
        payment_method: str,
        chat_id: Optional[int] = None,
        telegram_payment_id: Optional[str] = None,
        screenshot_file_id: Optional[str] = None
    ) -> Payment:
        """
        Create a payment record in database.
        
        Args:
            user_id: User ID making payment
            tariff_id: Tariff being purchased
            amount: Payment amount
            payment_method: Method (telegram_stars, manual_card)
            chat_id: Optional chat ID for channel/group subscriptions
            telegram_payment_id: Telegram payment charge ID
            screenshot_file_id: Screenshot file ID for manual payments
        
        Returns:
            Payment record
        """
        async with get_session() as session:
            payment = Payment(
                user_id=user_id,
                chat_id=chat_id,
                tariff_id=tariff_id,
                amount=amount,
                currency='USD',
                payment_method=payment_method,
                status='pending',
                telegram_payment_id=telegram_payment_id,
                screenshot_file_id=screenshot_file_id
            )
            session.add(payment)
            await session.flush()
            
            payment_id = payment.id
            await session.commit()
        
        logger.info(f"Created payment record {payment_id} for user {user_id}")
        return payment
    
    @staticmethod
    async def approve_payment(payment_id: int, approved_by_user_id: int) -> Subscription:
        """
        Approve a payment and create subscription.
        
        Args:
            payment_id: Payment ID to approve
            approved_by_user_id: Admin user ID who approved
        
        Returns:
            Created subscription
        """
        async with get_session() as session:
            from sqlalchemy import select, update
            
            # Get payment
            result = await session.execute(
                select(Payment).where(Payment.id == payment_id)
            )
            payment = result.scalar_one()
            
            # Update payment status
            await session.execute(
                update(Payment)
                .where(Payment.id == payment_id)
                .values(
                    status='approved',
                    approved_by_user_id=approved_by_user_id,
                    updated_at=datetime.now()
                )
            )
            
            # Create subscription
            subscription = await SubscriptionRepository.create(
                session,
                user_id=payment.user_id,
                chat_id=payment.chat_id,
                tariff_id=payment.tariff_id,
                duration_months=1
            )
            
            await session.commit()
        
        logger.info(
            f"Payment {payment_id} approved by user {approved_by_user_id}, "
            f"subscription {subscription.id} created"
        )
        return subscription
    
    @staticmethod
    async def reject_payment(payment_id: int, admin_user_id: int, reason: str):
        """
        Reject a payment.
        
        Args:
            payment_id: Payment ID to reject
            admin_user_id: Admin user ID who rejected
            reason: Rejection reason
        """
        async with get_session() as session:
            from sqlalchemy import update
            
            await session.execute(
                update(Payment)
                .where(Payment.id == payment_id)
                .values(
                    status='rejected',
                    approved_by_user_id=admin_user_id,
                    notes=reason,
                    updated_at=datetime.now()
                )
            )
            await session.commit()
        
        logger.info(f"Payment {payment_id} rejected by admin {admin_user_id}")
    
    @staticmethod
    async def get_pending_payments() -> list[Payment]:
        """Get all pending manual payments for admin review."""
        async with get_session() as session:
            from sqlalchemy import select
            
            result = await session.execute(
                select(Payment)
                .where(Payment.status == 'pending')
                .where(Payment.payment_method == 'manual_card')
                .order_by(Payment.created_at.desc())
            )
            return list(result.scalars().all())
    
    @staticmethod
    async def process_telegram_payment(
        user_id: int,
        tariff_id: int,
        telegram_payment_id: str,
        amount: Decimal
    ) -> Subscription:
        """
        Process successful Telegram Stars payment.
        Auto-approve and create subscription.
        
        Args:
            user_id: User ID
            tariff_id: Tariff purchased
            telegram_payment_id: Telegram payment charge ID
            amount: Payment amount
        
        Returns:
            Created subscription
        """
        async with get_session() as session:
            # Create payment record
            payment = Payment(
                user_id=user_id,
                tariff_id=tariff_id,
                amount=amount,
                currency='USD',
                payment_method='telegram_stars',
                status='approved',
                telegram_payment_id=telegram_payment_id
            )
            session.add(payment)
            await session.flush()
            
            # Create subscription immediately (auto-approved)
            subscription = await SubscriptionRepository.create(
                session,
                user_id=user_id,
                chat_id=None,
                tariff_id=tariff_id,
                duration_months=1
            )
            
            await session.commit()
        
        logger.info(
            f"Telegram payment processed for user {user_id}, "
            f"subscription {subscription.id} created"
        )
        return subscription
