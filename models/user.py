from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class Master(Base):
    __tablename__ = "masters"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    timezone = Column(String, nullable=False, server_default="Europe/Moscow")
    telegram_id = Column(BigInteger, nullable=True, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    services = relationship("Service", back_populates="master")
    subscription = relationship("Subscription", back_populates="master")
    schedules = relationship("WorkSchedule", back_populates="master")
    bookings = relationship("Booking", back_populates="master")
    schedule_exceptions = relationship(
        "ScheduleException", back_populates="master", cascade="all, delete-orphan"
    )
    password_reset_tokens = relationship(
        "PasswordResetToken", back_populates="master", cascade="all, delete-orphan"
    )
