from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Game(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    date = Column(String(200))
    time = Column(String(200))
    tbd = Column(Boolean, default=False)
    visiting_long_name = Column(String(200), nullable=True)
    visiting_short_name = Column(String(200), nullable=True)
    visiting_full_name = Column(String(200), nullable=True)
    visiting_record = Column(String(200), nullable=True)
    home_long_name = Column(String(200), nullable=True)
    home_short_name = Column(String(200), nullable=True)
    home_full_name = Column(String(200), nullable=True)
    home_record = Column(String(200), nullable=True)
    stadium = Column(String(200), nullable=True)
    city = Column(String(200), nullable=True)
    state = Column(String(200), nullable=True)
    visiting_pitchers = Column(String(1000), nullable=True)
    home_pitchers = Column(String(1000), nullable=True)
    home_last_games = Column(String(200), nullable=True)
    visiting_last_games = Column(String(200), nullable=True)
