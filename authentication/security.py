import jwt
import bcrypt
from dotenv import load_dotenv
import os
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, Header

from base.database import get_db
from base.models import User

load_dotenv('.env')
SECRET_KEY_JWT = os.getenv('SECRET_KEY_JWT')


def create_jwt_token(user_data: dict, secret_key: str):
    """
    Создание JWT токена
    """
    token = jwt.encode(user_data, secret_key, algorithm="HS256")
    return token


def extract_token(authorization: str) -> str:
    """
    Убираем Bearer если есть
    """
    if authorization.startswith('Bearer '):
        return authorization[7:]
    return authorization


def decoded_token(token: str, db: Session):
    """
    Получаем из JWT токена user id и возвращаем объект User
    """
    try:
        decoded_token = jwt.decode(extract_token(token), SECRET_KEY_JWT, algorithms=["HS256"])
        user_id = decoded_token["id"]
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Пользователь не авторизован")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Ошибка аутентификации")



def get_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    user = decoded_token(authorization, db)
    if user:
        return user



def hash_password(password: str) -> bytes:
    """
    Хэширование пароля
    """
    salt = bcrypt.gensalt()
    bytes = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(bytes, salt)
    return hashed_password


def check_password(entered_password: str, hashed_password_from_db: str) -> bool:
    """
    Проверка введенного пароля с хешируемым значением в базе
    """
    binary_data = hashed_password_from_db.encode("utf-8")
    return bcrypt.checkpw(entered_password.encode("utf-8"), binary_data)
