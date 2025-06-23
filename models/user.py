from sqlalchemy import Column, String, BigInteger
from db import Base

class User(Base):
    __tablename__ = "users"

    username: str = Column(String, primary_key=True, index=True)
    chat_id: int = Column(BigInteger, unique=True, nullable=False)
    first_name: str | None = Column(String, nullable=True)
    last_name: str | None = Column(String, nullable=True)
    save_link: str | None = Column(String, nullable=True)