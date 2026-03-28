from sqlalchemy import Column, Integer, Date, Time, String, ForeignKey
from sqlalchemy.orm import relationship

from core.database import Base


class ScheduleException(Base):
    __tablename__ = "schedule_exceptions"

    id = Column(Integer, primary_key=True)
    master_id = Column(
        Integer, ForeignKey("masters.id", ondelete="CASCADE"), nullable=False
    )
    date = Column(Date, nullable=False)
    type = Column(String, nullable=False)  # "dayoff" | "block"
    start_time = Column(Time, nullable=True)  # только для type="block"
    end_time = Column(Time, nullable=True)  # только для type="block"

    master = relationship("Master", back_populates="schedule_exceptions")
