"""
Seed initial data into the database.
Creates default tariff plans.
"""

import asyncio
from decimal import Decimal

from database import get_session
from database.models import Tariff
from bot.logger import setup_logging, get_logger

setup_logging("INFO")
logger = get_logger(__name__)


async def seed_tariffs():
    """Create default tariff plans."""
    logger.info("Seeding tariff plans...")
    
    tariffs = [
        {
            "name": "free_dm",
            "price": Decimal("0.00"),
            "currency": "USD",
            "limits": {"tts_per_month": 3, "max_text_length": 4500},
            "is_visible": True,
            "description": "Free tier: 3 TTS per month for direct messages"
        },
        {
            "name": "paid_dm",
            "price": Decimal("10.00"),
            "currency": "USD",
            "limits": {"tts_per_month": -1, "max_text_length": 4500},  # -1 = unlimited
            "is_visible": True,
            "description": "Paid DM: Unlimited TTS for direct messages - $10/month"
        },
        {
            "name": "paid_channel",
            "price": Decimal("10.00"),
            "currency": "USD",
            "limits": {"tts_per_month": -1, "max_text_length": 4500},
            "is_visible": True,
            "description": "Paid Channel: Unlimited TTS for channels/groups - $10/month"
        },
        {
            "name": "vip",
            "price": Decimal("0.00"),
            "currency": "USD",
            "limits": {"tts_per_month": -1, "max_text_length": 4500},
            "is_visible": False,
            "description": "VIP: Unlimited everything (admin-assigned only)"
        }
    ]
    
    async with get_session() as session:
        for tariff_data in tariffs:
            # Check if exists
            from sqlalchemy import select
            result = await session.execute(
                select(Tariff).where(Tariff.name == tariff_data["name"])
            )
            existing = result.scalar_one_or_none()
            
            if existing is None:
                tariff = Tariff(**tariff_data)
                session.add(tariff)
                logger.info(f"Created tariff: {tariff_data['name']}")
            else:
                logger.info(f"Tariff already exists: {tariff_data['name']}")
        
        await session.commit()
    
    logger.info("Tariff seeding complete!")


async def main():
    """Run all seed operations."""
    logger.info("Starting database seeding...")
    
    try:        
        await seed_tariffs()
        logger.info("✅ Database seeding completed successfully!")
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
