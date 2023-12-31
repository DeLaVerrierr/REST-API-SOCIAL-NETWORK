from datetime import datetime

from pydantic import BaseModel


class RegisterUser(BaseModel):
    name: str
    surname: str
    mail: str
    password: str


class LoginUser(BaseModel):
    mail: str
    password: str


class UserProfile(BaseModel):
    name: str
    surname: str
    mail: str
    friends: list


class CreatePost(BaseModel):
    text: str


class ChangePost(BaseModel):
    new_text: str


class ViewPost(BaseModel):
    id: int
    text: str
    created_at: str
    user_id: int
    like_count: int
    likes: list


class Feed(BaseModel):
    id: int
    text: str
    created_at: str
    user_id: int
    like_count: int


class CreateCommentPost(BaseModel):
    text: str


class ChangeComment(BaseModel):
    new_text: str


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


class SendMessage(BaseModel):
    text: str


class MessageResponse(BaseModel):
    id: int
    sender_name: str
    accepted_name: str
    text: str
    created_at: str
    status: str


class ViewBlacklist(BaseModel):
    user_id: int
    name: str
    surname: str
