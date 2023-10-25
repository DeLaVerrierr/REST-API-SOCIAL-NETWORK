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
