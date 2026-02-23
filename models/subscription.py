from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func 
from core.database import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    master_id = Column(Integer, ForeignKey("masters.id"), nullable=False, index=True)
    plan = Column(String, default="free") # Тип подписки: free, pro
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=True) # Дата окончания подписки
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    master = relationship("Master", back_populates="subscription")