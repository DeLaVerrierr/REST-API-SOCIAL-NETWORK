import base64
import binascii
import json

import jwt
import bcrypt
from dotenv import load_dotenv
import os
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, Header
from base.database import get_db
from base.models import User
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

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


##########################################################

private_keys_file = 'private_keys.json'


def save_to_private_keys(data):
    try:
        with open(private_keys_file, 'r') as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.append(data)

    with open(private_keys_file, 'w') as file:
        json.dump(existing_data, file)


def load_private_key_from_data(private_key_base64):
    private_key_pem = base64.b64decode(private_key_base64)
    private_key = serialization.load_pem_private_key(private_key_pem, password=None, backend=default_backend())
    return private_key


def load_public_key_from_pem(pem_bytes):
    # Сериализируем публичный ключ формата PEM
    public_key = serialization.load_pem_public_key(pem_bytes, backend=default_backend())
    return public_key


def encrypt_test(message, public_key):
    """
    Шифровка сообщение
    """
    # Сериализация ключа из базы
    public_key = load_public_key_from_pem(public_key)
    encrypted_message = public_key.encrypt(
        message.encode('utf-8'),  # Переводим текст в байты
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return encrypted_message


def load_private_key_from_file(user_id):
    with open(private_keys_file, 'r') as file:
        private_keys = json.load(file)

    for user_list in private_keys:
        for user_info in user_list:
            if user_info.get("user_id") == user_id:
                private_key_data = user_info.get("private_key")
                # private_key = load_private_key_from_data(private_key_data)
                return private_key_data
    return None


def byte_string(string):
    hex_string = string.replace('\\x', '').replace(' ', '')

    # Преобразование в байтовую строку
    byte_string = binascii.unhexlify(hex_string)
    return byte_string


def decrypt_test(encrypted_message, private_key):
    """
    Расшифровка сообщение
    """
    decrypted_message = private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_message


def generate_rsa_key_pair():
    # Генерация ключей
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    public_key = private_key.public_key()

    return private_key, public_key


def result_message():
    sender_id = message_object.sender_id
    # Получаем из json файла приватный ключ
    key_from_json = load_private_key_from_file(sender_id)  # Проверил все совпадает с json
    print(f"Получаем приватный ключ str из json {key_from_json}")
    print('----------------')
    # Делаем из него объект криптографии
    private_key = load_private_key_from_data(key_from_json)
    print(f"Делаем из str объект криптографии {private_key}")
    print('----------------')
    print(f"Сообщение которое надо расшифровать {message_object.text}")
    print('----------------')
    print(f"Приватный ключ который мы используем для расшифровки {private_key}")
    print('----------------')
    b_message = byte_string(message_object.text)
    message_result = decrypt_test(b_message, private_key)

    message_result_str = message_result.decode('utf-8')
    print(f"Расшифрованное сообщение {message_result_str}")
    return {"meadsf": "fdsfds"}