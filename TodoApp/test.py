# coding: utf-8
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True)
    username = Column(String(45), unique=True)
    first_name = Column(String(45))
    last_name = Column(String(45))
    hashed_password = Column(String(200))
    is_active = Column(Boolean)


class Todo(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    description = Column(String(200))
    priority = Column(Integer)
    complete = Column(Boolean)
    owner_id = Column(ForeignKey('users.id'))

    owner = relationship('User')
