"""
Bot commands and callback handlers.
Handles /start, help, and menu interactions.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from .logger import get_logger

logger = get_logger(__name__)

# Create router for commands
router = Router()


def get_main_menu() -> InlineKeyboardMarkup:
    """Get main menu keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎙️ Convert to Speech (TTS)", callback_data="tts_mode")],
        [InlineKeyboardButton(text="ℹ️ Help & Info", callback_data="help")],
    ])


def get_back_button() -> InlineKeyboardMarkup:
    """Get back to menu button."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="menu")],
    ])


@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Handle /start command.
    Shows welcome message and main menu.
    """
    logger.info(f"User {message.from_user.id} started the bot")
    
    await message.answer(
        "🎙️ **Salom! / Салом!**\n\n"
        "I'm an Uzbek Text-to-Speech bot. I can:\n"
        "✅ Convert Uzbek text to speech (Latin & Cyrillic)\n"
        "✅ Handle numbers (25 → йигирма беш)\n"
        "✅ Spell acronyms (USA → у-эс-а)\n"
        "✅ Support ordinals (9- → тўққиз инчи)\n\n"
        "Choose an option below:",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    await callback_help_handler(message)


@router.callback_query(F.data == "menu")
async def callback_menu(callback: CallbackQuery):
    """Handle back to menu button."""
    await callback.message.edit_text(
        "🎙️ **Salom! / Салом!**\n\n"
        "I'm an Uzbek Text-to-Speech bot. I can:\n"
        "✅ Convert Uzbek text to speech (Latin & Cyrillic)\n"
        "✅ Handle numbers (25 → йигирма беш)\n"
        "✅ Spell acronyms (USA → у-эс-а)\n"
        "✅ Support ordinals (9- → тўққиз инчи)\n\n"
        "Choose an option below:",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "tts_mode")
async def callback_tts_mode(callback: CallbackQuery):
    """Handle TTS mode button click."""
    logger.info(f"User {callback.from_user.id} activated TTS mode")
    
    await callback.message.edit_text(
        "🎙️ **TTS Mode Active**\n\n"
        "Send me any Uzbek text and I'll convert it to speech!\n\n"
        "**Features:**\n"
        "• Both Latin and Cyrillic scripts\n"
        "• Numbers converted to words\n"
        "• Acronyms spelled out\n"
        "• Ordinal numbers (9-yanvar)\n\n"
        "**Examples:**\n"
        "• `Salom dunyo!`\n"
        "• `Men 25 yoshdaman`\n"
        "• `9-yanvar kuni`\n"
        "• `USA prezidenti`\n\n"
        "Just send your text now! 👇",
        reply_markup=get_back_button(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery):
    """Handle help button click."""
    await callback_help_handler(callback.message, is_callback=True)
    await callback.answer()


async def callback_help_handler(message: Message, is_callback: bool = False):
    """
    Show help information.
    
    Args:
        message: Message object
        is_callback: If True, edit message instead of sending new one
    """
    help_text = (
        "ℹ️ **Help & Information**\n\n"
        "**How to use:**\n"
        "1. Click \"🎙️ TTS\" button\n"
        "2. Send any Uzbek text\n"
        "3. Receive audio!\n\n"
        "**Supported features:**\n"
        "✅ Latin script: `Salom dunyo`\n"
        "✅ Cyrillic script: `Салом дунё`\n"
        "✅ Numbers: `25` → \"йигирма беш\"\n"
        "✅ Ordinals: `9-yanvar` → \"тўққиз инчи yanvar\"\n"
        "✅ Acronyms: `USA` → \"у-эс-а\"\n"
        "✅ Long text (auto-split)\n\n"
        "**Channel mode:**\n"
        "You can also add me to a channel as admin.\n"
        "I'll convert messages with `#audio` hashtag.\n\n"
        "**Open source:**\n"
        "100% free, using Facebook MMS VITS model."
    )
    
    if is_callback:
        await message.edit_text(
            help_text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            help_text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
