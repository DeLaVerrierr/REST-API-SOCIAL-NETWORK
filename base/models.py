from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    surname = Column(String, index=True)
    mail = Column(String, index=True)
    password = Column(String, index=True)
    status = Column(String, default='user')

    posts = relationship("Post", back_populates="user")



class Post(Base):
    __tablename__ = "Post"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    created_at = Column(DateTime, default=func.now())

    user_id = Column(Integer, ForeignKey('User.id'))

    user = relationship("User", back_populates="posts")


