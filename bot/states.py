"""
User state management for tracking user interactions.
Simple in-memory state tracking.
"""

from typing import Dict
from .logger import get_logger

logger = get_logger(__name__)

# User states: user_id -> current_mode
# Possible states: 'idle', 'tts_mode'
_user_states: Dict[int, str] = {}


def set_user_state(user_id: int, state: str):
    """
    Set user's current state.
    
    Args:
        user_id: Telegram user ID
        state: State name ('idle', 'tts_mode', etc.)
    """
    _user_states[user_id] = state
    logger.debug(f"User {user_id} state set to: {state}")


def get_user_state(user_id: int) -> str:
    """
    Get user's current state.
    
    Args:
        user_id: Telegram user ID
    
    Returns:
        Current state, defaults to 'tts_mode' for simplicity
    """
    # Default to tts_mode so users can just send text immediately
    return _user_states.get(user_id, 'tts_mode')


def clear_user_state(user_id: int):
    """
    Clear user's state.
    
    Args:
        user_id: Telegram user ID
    """
    if user_id in _user_states:
        del _user_states[user_id]
        logger.debug(f"Cleared state for user {user_id}")
