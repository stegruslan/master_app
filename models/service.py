from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    master_id = Column(Integer, ForeignKey("masters.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)  # Длительность в минутах
    price = Column(Integer, nullable=False)  # Цена в рублях 
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    master = relationship("Master", back_populates="services")
    bookings = relationship("Booking", back_populates="service")