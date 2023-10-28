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
    Проверяем токен JWT
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
    """
    Возвращает объект user
    """
    user = decoded_token(authorization, db)
    if user:
        return user



def hash_object(object: str) -> bytes:
    """
    Хэширование пароля
    """
    salt = bcrypt.gensalt()
    bytes = object.encode('utf-8')
    hashed_password = bcrypt.hashpw(bytes, salt)
    return hashed_password


def check_password(entered_password: str, hashed_object_from_db: str) -> bool:
    """
    Проверка введенного пароля с хешируемым значением в базе
    """
    binary_data = hashed_object_from_db.encode("utf-8")
    return bcrypt.checkpw(entered_password.encode("utf-8"), binary_data)




abc = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяabcdefghijklmnopqrstuvwxyz'
def encrypt_caesar(message, key):
    """
    Шифровка сообщение
    """
    count = len(abc)
    result = ""
    for letter in message:
        if letter.lower() in abc:
            is_upper = letter.isupper()
            letter = letter.lower()
            idx = abc.index(letter)
            new_idx = (idx + key) % count
            new_letter = abc[new_idx]
            if is_upper:
                new_letter = new_letter.upper()
            result += new_letter
        else:
            result += letter
    return result

def decrypt_caesar(message, key):
    """
    Расшифровка сообщение
    """
    return encrypt_caesar(message, -key)




