from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.dependencies import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    posts = relationship("PostModel", back_populates="user")