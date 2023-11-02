import json

import jwt
import bcrypt
from dotenv import load_dotenv
import os
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, Header
from base.database import get_db
from base.models import User, Message
import rsa

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


##########################################################

private_keys_file = 'private_keys.json'


def save_to_private_keys(data):
    """
    Сохранение ключей в json файл
    """
    try:
        with open(private_keys_file, 'r') as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.append(data)

    with open(private_keys_file, 'w') as file:
        json.dump(existing_data, file)


def load_private_key_from_file(user_id):
    """
    Выводим секретный ключ по user_id
    """
    with open(private_keys_file, 'r') as file:
        private_keys = json.load(file)

    for user_list in private_keys:
        for user_info in user_list:
            if user_info.get("user_id") == user_id:
                print(f"Вытаскиваем из json ключ айди {user_id}")
                private_key_data = user_info.get("private_key")
                print(f'Приватный ключ айди {user_id} вот такой {private_key_data}')
                return private_key_data
    return None


def generate_rsa_key_pair():
    """
    Генерация ключей
    """
    (pubkey, privkey) = rsa.newkeys(512)
    # Преобразование ключей в строковое представление PEM
    pubkey_str = pubkey.save_pkcs1().decode()
    privkey_str = privkey.save_pkcs1().decode()
    return privkey_str, pubkey_str






# import rsa
# (pubkey, privkey) = rsa.newkeys(512)
# # Преобразование ключей в строковое представление PEM
# pubkey_str = pubkey.save_pkcs1().decode()
# privkey_str = privkey.save_pkcs1().decode()
# print(pubkey)
# # Теперь можно сохранить pubkey_str и privkey_str в базу данных
#
# loaded_pubkey = rsa.PublicKey.load_pkcs1(pubkey_str.encode())
# loaded_privkey = rsa.PrivateKey.load_pkcs1(privkey_str.encode())
# print(loaded_pubkey)
# my_str = 'Hello'
#
# message = str.encode(my_str)
# # шифруем
# crypto = rsa.encrypt(message, pubkey)
# print(crypto)
# #расшифровываем
# message = rsa.decrypt(crypto, privkey)
# print(message)


# 2 Amir eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Mn0.FiAR5ShqvInBbMOsiDbx9VKI7DZPyPHC8181YV5bHQs
# 3 Vadim    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6M30.bkSLi1o9LmUdlv7Fux44ciOy9keDX96-AZdCihkl4fM
