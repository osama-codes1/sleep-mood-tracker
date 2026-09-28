from sqlalchemy import Column, Integer, Float, Date

from database import Base


class Entry(Base):
    """One night of sleep and the mood recorded for that day."""

    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True)
    sleep_hours = Column(Float, nullable=False)
    mood = Column(Integer, nullable=False)
