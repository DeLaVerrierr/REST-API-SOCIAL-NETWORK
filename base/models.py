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
    comments = relationship("Comment", back_populates="user")



class Comment(Base):
    __tablename__ = "Comment"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    created_at = Column(DateTime, default=func.now())

    user_id = Column(Integer, ForeignKey('User.id'))
    post_id = Column(Integer, ForeignKey('Post.id'))

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")


class Post(Base):
    __tablename__ = "Post"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    created_at = Column(DateTime, default=func.now())

    user_id = Column(Integer, ForeignKey('User.id'))

    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")


class Friend(Base):
    __tablename__ = "Friend"
    first_user_id = Column(Integer, ForeignKey('User.id'), primary_key=True)
    second_user_id = Column(Integer, ForeignKey('User.id'), primary_key=True)
    created_at = Column(DateTime, default=func.now())

class RequestFriend(Base):
    __tablename__ = "RequestFriend"
    id = Column(Integer, primary_key=True, index=True)
    first_user_id = Column(Integer, ForeignKey('User.id'))
    second_user_id = Column(Integer, ForeignKey('User.id'))
    status = Column(String, default='request')
    created_at = Column(DateTime, default=func.now())

