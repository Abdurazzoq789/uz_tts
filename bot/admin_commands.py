"""
Admin commands for user management and statistics.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from services.client_service import ClientService
from bot.config import get_config
from bot.logger import get_logger

logger = get_logger(__name__)

router = Router()


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Show user statistics."""
    try:
        stats = await ClientService.get_user_stats(message.from_user.id)
        
        await message.answer(
            f"📊 **Your Statistics**\n\n"
            f"User ID: `{stats['user_id']}`\n"
            f"Status: {stats['status']}\n"
            f"This Month:\n"
            f"  • TTS Generated: {stats['monthly_tts_count']}\n"
            f"  • Characters: {stats['monthly_characters']:,}\n"
            f"Member Since: {stats['created_at'].strftime('%Y-%m-%d') if stats['created_at'] else 'N/A'}",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to get stats for user {message.from_user.id}: {e}")
        await message.answer("❌ Failed to retrieve statistics. Please try again later.")


@router.message(Command("admin_blacklist"))
async def cmd_admin_blacklist(message: Message):
    """Admin command to blacklist a user (via reply)."""
    config = get_config()
    
    # Check if user is admin
    if message.from_user.id not in config.get_admin_ids():
        return
    
    # Must be a reply
    if not message.reply_to_message or not message.reply_to_message.from_user:
        await message.answer("⚠️ Reply to a user's message to blacklist them.")
        return
    
    target_user_id = message.reply_to_message.from_user.id
    
    try:
        await ClientService.update_user_status(target_user_id, 'blacklisted')
        await message.answer(
            f"✅ User {target_user_id} has been blacklisted.\n"
            "They will no longer be able to use the bot."
        )
        logger.info(f"Admin {message.from_user.id} blacklisted user {target_user_id}")
    except Exception as e:
        logger.error(f"Failed to blacklist user {target_user_id}: {e}")
        await message.answer("❌ Failed to blacklist user.")


@router.message(Command("admin_unblacklist"))
async def cmd_admin_unblacklist(message: Message):
    """Admin command to unblacklist a user (via reply)."""
    config = get_config()
    
    if message.from_user.id not in config.get_admin_ids():
        return
    
    if not message.reply_to_message or not message.reply_to_message.from_user:
        await message.answer("⚠️ Reply to a user's message to unblacklist them.")
        return
    
    target_user_id = message.reply_to_message.from_user.id
    
    try:
        await ClientService.update_user_status(target_user_id, 'active')
        await message.answer(
            f"✅ User {target_user_id} has been unblacklisted.\n"
            "They can now use the bot again."
        )
        logger.info(f"Admin {message.from_user.id} unblacklisted user {target_user_id}")
    except Exception as e:
        logger.error(f"Failed to unblacklist user {target_user_id}: {e}")
        await message.answer("❌ Failed to unblacklist user.")


@router.message(Command("admin_info"))
async def cmd_admin_info(message: Message):
    """Admin command to get user info (via reply)."""
    config = get_config()
    
    if message.from_user.id not in config.get_admin_ids():
        return
    
    if not message.reply_to_message or not message.reply_to_message.from_user:
        await message.answer("⚠️ Reply to a user's message to get their info.")
        return
    
    target_user_id = message.reply_to_message.from_user.id
    
    try:
        stats = await ClientService.get_user_stats(target_user_id)
        
        await message.answer(
            f"👤 **User Information**\n\n"
            f"ID: `{stats['user_id']}`\n"
            f"Status: {stats['status']}\n"
            f"TTS Count (This Month): {stats['monthly_tts_count']}\n"
            f"Characters (This Month): {stats['monthly_characters']:,}\n"
            f"Registered: {stats['created_at'].strftime('%Y-%m-%d %H:%M') if stats['created_at'] else 'N/A'}",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to get info for user {target_user_id}: {e}")
        await message.answer("❌ Failed to retrieve user info.")
