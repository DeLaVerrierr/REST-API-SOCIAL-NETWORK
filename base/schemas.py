from pydantic import BaseModel
from typing import List

from base.models import Post


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


class ViewPost(BaseModel):
    id: int
    text: str
    created_at: str
    user_id: int


class CreateCommentPost(BaseModel):
    text: str
