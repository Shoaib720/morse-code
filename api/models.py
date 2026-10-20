from uuid import UUID, uuid4
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String(255))

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer,primary_key=True,index=True)
    userId = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="messages")
    message = Column(String(255))
    createdAt = Column(DateTime, default=func.now())
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now())
    