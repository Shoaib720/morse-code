from uuid import UUID, uuid4
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from .database import Base

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID,primary_key=True,index=True)
    message = Column(String(255))
    createdAt = Column(DateTime, default=func.now())
    