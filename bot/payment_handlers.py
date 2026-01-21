"""
Payment handlers for Telegram Stars and manual payments.
"""

from decimal import Decimal

from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, PreCheckoutQuery,
    LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
)

from services.payment_service import PaymentService
from database.repository import TariffRepository
from database import get_session
from bot.config import get_config
from bot.logger import get_logger

logger = get_logger(__name__)

router = Router()


@router.callback_query(F.data == "pay:telegram_stars")
async def handle_telegram_stars_payment(callback: CallbackQuery):
    """Initiate Telegram Stars payment."""
    config = get_config()
    
    if not config.telegram_payment_enabled:
        await callback.answer("⚠️ Telegram payment is currently unavailable", show_alert=True)
        return
    
    # Get paid_dm tariff
    async with get_session() as session:
        tariff = await TariffRepository.get_by_name(session, 'paid_dm')
    
    if not tariff:
        await callback.answer("❌ Payment configuration error", show_alert=True)
        return
    
    # Create invoice
    prices = [LabeledPrice(
        label=f"{tariff.description}",
        amount=int(float(tariff.price) * 100)  # Convert to stars (cents)
    )]
    
    try:
        await callback.message.answer_invoice(
            title="Uzbek TTS Premium Subscription",
            description=f"{tariff.description}\n\nUnlimited TTS for 1 month",
            payload=f"tariff_{tariff.id}_user_{callback.from_user.id}",
            provider_token="",  # Empty for Telegram Stars
            currency="XTR",  # Telegram Stars currency code
            prices=prices,
            start_parameter="subscription"
        )
        
        await callback.answer("✅ Invoice sent!")
        logger.info(f"Telegram Stars invoice sent to user {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"Failed to send invoice: {e}", exc_info=True)
        await callback.answer("❌ Failed to create invoice", show_alert=True)


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    """
    Handle pre-checkout query.
    This is called by Telegram before processing payment.
    """
    logger.info(f"Pre-checkout query from user {pre_checkout_query.from_user.id}")
    
    # Always approve (we'll verify on successful_payment)
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    """
    Handle successful Telegram Stars payment.
    Create subscription automatically.
    """
    payment_info = message.successful_payment
    
    # Parse payload to get tariff_id
    # Format: "tariff_{id}_user_{user_id}"
    try:
        parts = payment_info.invoice_payload.split('_')
        tariff_id = int(parts[1])
        
        # Process payment and create subscription
        subscription = await PaymentService.process_telegram_payment(
            user_id=message.from_user.id,
            tariff_id=tariff_id,
            telegram_payment_id=payment_info.telegram_payment_charge_id,
            amount=Decimal(payment_info.total_amount) / 100
        )
        
        await message.answer(
            "✅ **Payment Successful!**\n\n"
            "Your premium subscription is now active.\n"
            "Enjoy unlimited TTS! 🎉\n\n"
            f"Subscription valid until: {subscription.end_date.strftime('%Y-%m-%d')}",
            parse_mode="Markdown"
        )
        
        logger.info(
            f"User {message.from_user.id} successfully subscribed via Telegram Stars"
        )
        
    except Exception as e:
        logger.error(f"Failed to process payment: {e}", exc_info=True)
        await message.answer(
            "⚠️ Payment received but subscription activation failed.\n"
            "Please contact support with your payment ID."
        )


@router.message(F.photo & F.chat.type == "private")
async def handle_payment_screenshot(message: Message):
    """
    Handle payment screenshot for manual card payments.
    """
    photo = message.photo[-1]  # Get largest size
    
    try:
        config = get_config()
        
        # Get paid_dm tariff
        async with get_session() as session:
            tariff = await TariffRepository.get_by_name(session, 'paid_dm')
        
        if not tariff:
            logger.error("Tariff not found for manual payment")
            return
        
        # Create pending payment record
        payment = await PaymentService.create_payment_record(
            user_id=message.from_user.id,
            tariff_id=tariff.id,
            amount=Decimal(config.paid_monthly_price),
            payment_method='manual_card',
            screenshot_file_id=photo.file_id
        )
        
        await message.answer(
            "✅ **Payment Screenshot Received!**\n\n"
            f"Payment ID: `{payment.id}`\n\n"
            "Our admin will verify your payment within 24 hours.\n"
            "You'll receive a confirmation message once your subscription is activated.\n\n"
            "Thank you for upgrading! 🎉",
            parse_mode="Markdown"
        )
        
        # Notify admins (if configured)
        admin_ids = config.get_admin_ids()
        if admin_ids:
            for admin_id in admin_ids:
                try:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="✅ Approve",
                                callback_data=f"approve_payment:{payment.id}"
                            ),
                            InlineKeyboardButton(
                                text="❌ Reject",
                                callback_data=f"reject_payment:{payment.id}"
                            )
                        ]
                    ])
                    
                    await message.bot.send_photo(
                        chat_id=admin_id,
                        photo=photo.file_id,
                        caption=(
                            f"💳 **New Payment Screenshot**\n\n"
                            f"Payment ID: `{payment.id}`\n"
                            f"User: {message.from_user.first_name} "
                            f"(@{message.from_user.username})\n"
                            f"User ID: `{message.from_user.id}`\n"
                            f"Amount: ${config.paid_monthly_price}\n"
                            f"Tariff: {tariff.name}"
                        ),
                        reply_markup=keyboard,
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin_id}: {e}")
        
        logger.info(f"Manual payment screenshot received from user {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Failed to process payment screenshot: {e}", exc_info=True)
        await message.answer(
            "❌ Failed to process your screenshot.\n"
            "Please try again or contact support."
        )


@router.callback_query(F.data.startswith("approve_payment:"))
async def approve_payment_callback(callback: CallbackQuery):
    """Admin callback to approve payment."""
    config = get_config()
    
    # Check if user is admin
    if callback.from_user.id not in config.get_admin_ids():
        await callback.answer("⛔ Access denied", show_alert=True)
        return
    
    # Get payment ID
    payment_id = int(callback.data.split(':')[1])
    
    try:
        # Approve payment and create subscription
        subscription = await PaymentService.approve_payment(
            payment_id=payment_id,
            approved_by_user_id=callback.from_user.id
        )
        
        # Get payment to get user_id
        async with get_session() as session:
            from sqlalchemy import select
            from database.models import Payment
            result = await session.execute(
                select(Payment).where(Payment.id == payment_id)
            )
            payment = result.scalar_one()
        
        # Notify user
        await callback.message.bot.send_message(
            chat_id=payment.user_id,
            text=(
                "✅ **Payment Approved!**\n\n"
                "Your premium subscription is now active.\n"
                "Enjoy unlimited TTS! 🎉\n\n"
                f"Subscription valid until: {subscription.end_date.strftime('%Y-%m-%d')}"
            ),
            parse_mode="Markdown"
        )
        
        # Update admin message
        await callback.message.edit_caption(
            caption=f"{callback.message.caption}\n\n✅ **APPROVED** by @{callback.from_user.username}",
            parse_mode="Markdown"
        )
        
        await callback.answer("✅ Payment approved and subscription activated!")
        logger.info(f"Payment {payment_id} approved by admin {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"Failed to approve payment {payment_id}: {e}", exc_info=True)
        await callback.answer("❌ Failed to approve payment", show_alert=True)


@router.callback_query(F.data.startswith("reject_payment:"))
async def reject_payment_callback(callback: CallbackQuery):
    """Admin callback to reject payment."""
    config = get_config()
    
    # Check if user is admin
    if callback.from_user.id not in config.get_admin_ids():
        await callback.answer("⛔ Access denied", show_alert=True)
        return
    
    # Get payment ID
    payment_id = int(callback.data.split(':')[1])
    
    try:
        # Reject payment
        await PaymentService.reject_payment(
            payment_id=payment_id,
            admin_user_id=callback.from_user.id,
            reason="Rejected by admin"
        )
        
        # Get payment to get user_id
        async with get_session() as session:
            from sqlalchemy import select
            from database.models import Payment
            result = await session.execute(
                select(Payment).where(Payment.id == payment_id)
            )
            payment = result.scalar_one()
        
        # Notify user
        await callback.message.bot.send_message(
            chat_id=payment.user_id,
            text=(
                "❌ **Payment Rejected**\n\n"
                "Your payment screenshot could not be verified.\n"
                "Please ensure:\n"
                "• Payment amount matches\n"
                "• Transaction is complete\n"
                "• Screenshot is clear\n\n"
                "Try again or contact support for assistance."
            ),
            parse_mode="Markdown"
        )
        
        # Update admin message
        await callback.message.edit_caption(
            caption=f"{callback.message.caption}\n\n❌ **REJECTED** by @{callback.from_user.username}",
            parse_mode="Markdown"
        )
        
        await callback.answer("Payment rejected")
        logger.info(f"Payment {payment_id} rejected by admin {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"Failed to reject payment {payment_id}: {e}", exc_info=True)
        await callback.answer("❌ Failed to reject payment", show_alert=True)
