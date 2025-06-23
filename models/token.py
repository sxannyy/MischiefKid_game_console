from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base

class Token(Base):
    __tablename__ = "tokens"

    username = Column(String, ForeignKey("users.username"), primary_key=True)
    token_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User")