from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.dependencies import Base

class PostModel(Base):
  __tablename__ = "posts"

  id = Column(Integer, primary_key=True, index=True)
  text = Column(String(255),nullable=False)
  user_id = Column(Integer, ForeignKey("users.id"))
  user = relationship("UserModel", back_populates="posts")