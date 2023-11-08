from cryptography.hazmat.primitives import serialization
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary
from sqlalchemy.dialects.postgresql import BYTEA
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
    public_key = Column(String, index=True)

    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    sent_messages = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    accepted_messages = relationship("Message", back_populates="accepted", foreign_keys="Message.accepted_id")


class Message(Base):
    __tablename__ = "Message"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey('User.id'))
    accepted_id = Column(Integer, ForeignKey('User.id'))
    text = Column(String, nullable=False)
    status = Column(String, default='sent')
    created_at = Column(DateTime, default=func.now())

    sender = relationship("User", foreign_keys=[sender_id])
    accepted = relationship("User", foreign_keys=[accepted_id])


class Comment(Base):
    __tablename__ = "Comment"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    created_at = Column(DateTime, default=func.now())

    user_id = Column(Integer, ForeignKey('User.id'))
    post_id = Column(Integer, ForeignKey('Post.id'))

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")


class Blacklist(Base):
    __tablename__ = "Blacklist"

    id = Column(Integer, primary_key=True, index=True)
    who_added = Column(Integer, ForeignKey('User.id'))
    who_was_added = Column(Integer, ForeignKey('User.id'))


class Post(Base):
    __tablename__ = "Post"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    created_at = Column(DateTime, default=func.now())
    like_count = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey('User.id'))

    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    reactions = relationship("Reaction")


class Reaction(Base):
    __tablename__ = "Reaction"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('Post.id'))
    user_id = Column(Integer, ForeignKey('User.id'))


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
