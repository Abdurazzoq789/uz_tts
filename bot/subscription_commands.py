"""
Subscription management commands.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from services.subscription_service import SubscriptionService
from bot.config import get_config
from bot.logger import get_logger

logger = get_logger(__name__)

router = Router()


@router.message(Command("subscription"))
async def cmd_subscription(message: Message):
    """Show subscription information."""
    try:
        sub_info = await SubscriptionService.get_subscription_info(message.from_user.id)
        
        if sub_info:
            await message.answer(
                f"💳 **Your Subscription**\n\n"
                f"Plan: {sub_info['tariff_description']}\n"
                f"Price: ${sub_info['price']:.2f}/{sub_info['currency']}\n"
                f"Status: {'✅ Active' if sub_info['is_active'] else '❌ Inactive'}\n"
                f"Valid Until: {sub_info['end_date'].strftime('%Y-%m-%d')}\n"
                f"Days Remaining: {sub_info['days_remaining']}",
                parse_mode="Markdown"
            )
        else:
            config = get_config()
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="💳 View Plans",
                    callback_data="view_plans"
                )]
            ])
            
            await message.answer(
                "📋 **Free Tier**\n\n"
                f"You have {config.free_tier_tts_limit} free TTS per month.\n"
                "Upgrade for unlimited access!",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"Failed to get subscription for user {message.from_user.id}: {e}")
        await message.answer("❌ Failed to retrieve subscription info.")


@router.callback_query(F.data == "view_plans")
async def callback_view_plans(callback: CallbackQuery):
    """Show available subscription plans."""
    config = get_config()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"💎 Subscribe - ${config.paid_monthly_price}/month",
            callback_data="subscribe"
        )],
        [InlineKeyboardButton(
            text="⬅️ Back",
            callback_data="menu"
        )]
    ])
    
    await callback.message.edit_text(
        "💳 **Subscription Plans**\n\n"
        "**🆓 Free Tier**\n"
        f"• {config.free_tier_tts_limit} TTS per month\n"
        "• Direct messages only\n\n"
        "**💎 Premium Plan**\n"
        f"• ${config.paid_monthly_price}/month\n"
        "• Unlimited TTS\n"
        "• Works in channels & groups\n"
        "• Priority support",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "subscribe")
async def callback_subscribe(callback: CallbackQuery):
    """Handle subscription request."""
    config = get_config()
    
    if config.telegram_payment_enabled:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="⭐ Pay with Telegram Stars",
                callback_data="pay:telegram_stars"
            )],
            [InlineKeyboardButton(
                text="💳 Manual Card Payment",
                callback_data="pay:manual_card"
            )],
            [InlineKeyboardButton(
                text="⬅️ Back",
                callback_data="view_plans"
            )]
        ])
        
        await callback.message.edit_text(
            "💰 **Choose Payment Method**\n\n"
            f"Price: ${config.paid_monthly_price}/month\n\n"
            "Select your preferred payment method:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            "⚠️ Payment system is currently under maintenance.\n"
            "Please try again later or contact support."
        )
    
    await callback.answer()


@router.callback_query(F.data == "pay:manual_card")
async def callback_manual_payment(callback: CallbackQuery):
    """Show manual card payment instructions."""
    config = get_config()
    
    if not config.manual_payment_card_number:
        await callback.answer("❌ Manual payment is not configured", show_alert=True)
        return
    
    await callback.message.edit_text(
        "💳 **Manual Card Payment**\n\n"
        f"Card Number: `{config.manual_payment_card_number}`\n"
        f"Card Holder: {config.manual_payment_card_holder}\n"
        f"Amount: ${config.paid_monthly_price}\n\n"
        "After payment, send a screenshot of the transfer to this chat.\n"
        "Our admin will verify and activate your subscription within 24 hours.",
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(F.photo)
async def handle_payment_screenshot(message: Message):
    """Handle payment screenshot submissions."""
    # Simple implementation - just log it
    # Full implementation would store in database with pending payment
    logger.info(f"Payment screenshot received from user {message.from_user.id}")
    
    await message.answer(
        "✅ **Payment Screenshot Received!**\n\n"
        "Our admin will verify your payment and activate your subscription within 24 hours.\n"
        "You'll receive a confirmation message once it's activated.\n\n"
        "Thank you for upgrading! 🎉"
    )
