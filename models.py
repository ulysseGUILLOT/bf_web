from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from init_db import Base
from datetime import datetime


class GamesUsers(Base):
    __tablename__ = 'games_users'
    game_id = Column(ForeignKey('games.id'), primary_key=True)
    user_id = Column(ForeignKey('users.id'), primary_key=True)
    team = Column(Integer)
    game = relationship('Game', back_populates='users')
    user = relationship('User', back_populates='games')

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    matches = Column(Integer, default=0)
    goals_total = Column(Integer, default=0)
    bounce_out_total = Column(Integer, default=0)
    games = relationship('GamesUsers', back_populates='user')

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return f'<User {self.username!r}>'
    
class Game(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    duration = Column(Integer, default=0)
    users = relationship('GamesUsers', back_populates='game')
    white_score = Column(Integer, default=0)
    black_score = Column(Integer, default=0)
    finished = Column(Boolean, default=False)
    