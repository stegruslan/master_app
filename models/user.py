from sqlalchemy import Column, Integer, String, Boolean, DateTime
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True),server_default=func.now(), onupdate=func.now()) 

    service = relationship("Service", back_populates="master")
    subscription = relationship("Subscription", back_populates="master")
    shedule = relationship("WorkSchedule", back_populates="master")
    bookings = relationship("Booking", back_populates="master")
