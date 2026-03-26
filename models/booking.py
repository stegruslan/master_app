from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    master_id = Column(Integer, ForeignKey("masters.id"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, index=True)

    # данные клиента
    client_name = Column(String, nullable=False)
    client_phone = Column(String, nullable=False)
    client_email = Column(String, nullable=True)

    # время записи
    datetime_start = Column(DateTime(timezone=True), nullable=False)
    datetime_end = Column(DateTime(timezone=True), nullable=False)

    # статус и токен отмены
    status = Column(String, default="pending")  #  # pending / confirmed / cancelled
    cancel_token = Column(String, unique=True, index=True, nullable=True)

    reminder_sent = Column(
        Boolean, default=False
    )  # Флаг для отслеживания отправки напоминания

    notes = Column(String, nullable=True)  # заметки для мастера

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    master = relationship("Master", back_populates="bookings")
    service = relationship("Service", back_populates="bookings")
