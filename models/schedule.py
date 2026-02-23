from sqlalchemy import Column, Integer, Time, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from core.database import Base


class WorkSchedule(Base):
    __tablename__ = "work_schedules"

    id = Column(Integer, primary_key=True, index=True)
    master_id = Column(Integer, ForeignKey("masters.id"), nullable=False, index=True)
    weekday = Column(Integer, nullable=False)  # 0 - Понедельник, 6 - Воскресенье
    start_time = Column(Time, nullable=False)  
    end_time = Column(Time, nullable=False)     
    is_active = Column(Boolean, default=True)

    master = relationship("Master", back_populates="work_schedule")