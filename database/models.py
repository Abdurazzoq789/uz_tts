"""
Database models for Uzbek TTS Bot SaaS platform.
Uses SQLAlchemy 2.0 with async support.
"""

from datetime import datetime, timedelta
from typing import Optional
from decimal import Decimal

from sqlalchemy import (
    BigInteger, String, Text, Integer, Numeric, Boolean, 
    DateTime, Date, JSON, Index, ForeignKey
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class User(Base):
    """User model - tracks all bot users."""
    __tablename__ = "users"
    
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    language_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='active', index=True)
    tariff_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('tariffs.id'), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    
    # Relationships
    tariff: Mapped[Optional["Tariff"]] = relationship("Tariff", back_populates="users")
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription", back_populates="user", foreign_keys="Subscription.user_id"
    )
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="user")
    tts_history: Mapped[list["TTSHistory"]] = relationship("TTSHistory", back_populates="user")


class Chat(Base):
    """Chat model - tracks channels, groups, and private chats."""
    __tablename__ = "chats"
    
    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    chat_type: Mapped[str] = mapped_column(String(20), index=True)  # private, group, channel
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='active', index=True)
    tariff_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('tariffs.id'), nullable=True
    )
    created_by_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey('users.user_id'), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    
    # Relationships
    tariff: Mapped[Optional["Tariff"]] = relationship("Tariff")
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_user_id])
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription", back_populates="chat", foreign_keys="Subscription.chat_id"
    )


class Tariff(Base):
    """Tariff/plan model."""
    __tablename__ = "tariffs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default='USD')
    limits: Mapped[dict] = mapped_column(JSON, nullable=True)  # {"tts_per_month": 3}
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="tariff")
    subscriptions: Mapped[list["Subscription"]] = relationship("Subscription", back_populates="tariff")


class Subscription(Base):
    """Subscription model."""
    __tablename__ = "subscriptions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey('users.user_id'), nullable=True
    )
    chat_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey('chats.chat_id'), nullable=True
    )
    tariff_id: Mapped[int] = mapped_column(Integer, ForeignKey('tariffs.id'), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="subscriptions")
    chat: Mapped[Optional["Chat"]] = relationship("Chat", back_populates="subscriptions")
    tariff: Mapped["Tariff"] = relationship("Tariff", back_populates="subscriptions")
    
    __table_args__ = (
        Index('idx_subscriptions_active_date', 'is_active', 'end_date'),
    )


class Payment(Base):
    """Payment model."""
    __tablename__ = "payments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id'), nullable=False, index=True)
    chat_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    tariff_id: Mapped[int] = mapped_column(Integer, ForeignKey('tariffs.id'), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default='USD')
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False)  # telegram_stars, manual_card
    status: Mapped[str] = mapped_column(String(20), default='pending', index=True)  # pending, approved, rejected
    telegram_payment_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    screenshot_file_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    approved_by_user_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="payments")


class TTSHistory(Base):
    """TTS request history and job queue."""
    __tablename__ = "tts_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey('users.user_id'), nullable=True)  # Nullable for channel posts
    chat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('chats.chat_id'), nullable=False)
    original_text: Mapped[str] = mapped_column(String, nullable=False)
    processed_text: Mapped[str] = mapped_column(String, nullable=False)
    audio_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String, default='pending', index=True)  # pending, processing, completed, failed
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tts_history")
    
    __table_args__ = (
        Index('idx_tts_history_user_date', 'user_id', 'created_at'),
    )


class UsageStats(Base):
    """Usage statistics tracking."""
    __tablename__ = "usage_stats"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    chat_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    period_start: Mapped[datetime] = mapped_column(Date, nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(Date, nullable=False)
    tts_count: Mapped[int] = mapped_column(Integer, default=0)
    total_characters: Mapped[int] = mapped_column(Integer, default=0)
    
    __table_args__ = (
        Index('idx_usage_unique_period', 'user_id', 'chat_id', 'period_start', unique=True),
    )
