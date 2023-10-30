import binascii
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import asc, or_
import random
from base.database import get_db
from sqlalchemy.orm import Session
from base.models import User, Message
from base.schemas import MessageView
from authentication.security import get_user, encrypt_caesar, decrypt_caesar, encrypt_test, decrypt_test, \
    load_private_key_from_file, load_private_key_from_data,byte_string

from base.schemas import SendMessage
from cryptography.fernet import Fernet
import psycopg2

router = APIRouter()


# 29           eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Mjl9.Ly8hkNipCTknlhOmIpYMAlSPC1J_1BOSun-MwgnK-So
# 30           eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MzB9.93zzmblAcQ-6Oj0bYYLcVUMrjvolFuCsl1P5DRsimtM


# http://127.0.0.1:8000/api/v1/social-network/user/message/{user_id}/send
@router.post('/{user_id}/send', summary='SendMessage', response_model=dict)
def send_message(user_id: int, message: SendMessage, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Отправка сообщение по user_id
    """
    accepted_user = db.query(User).filter(User.id == user_id).first()

    if accepted_user:
        message = encrypt_test(message.text, accepted_user.public_key)

        new_message = Message(sender_id=user.id, accepted_id=user_id, text=message)
        db.add(new_message)
        db.commit()

        return {"message": "Сообщение успешно отправлено"}
    raise HTTPException(status_code=404, detail="Пользователь не найден")


# @router.post('/{user_id}/send', summary='SendMessage', response_model=dict)
# def send_message(user_id: int, message: SendMessage, user: User = Depends(get_user), db: Session = Depends(get_db)):
#     """
#     Отправка сообщение по user_id
#     """
#     accepted_user = db.query(User).filter(User.id == user_id)
#
#     if accepted_user:
#         # Рандомный ключ шифрования
#         random_number = random.randint(1, 100)
#         print(random_number)
#         # Шифруем текст
#         encrypt_message = encrypt_caesar(message.text, random_number)
#         new_message = Message(sender_id=user.id, accepted_id=user_id, text=encrypt_message, key=random_number)
#         print(new_message.key)
#         db.add(new_message)
#         db.commit()
#         return {"message": "Сообщение успешно отправлено"}
#     raise HTTPException(status_code=404, detail="Пользователь не найден")


@router.get('/{user_id}', summary='SendMessage', response_model=list[MessageView])
def message_view(user_id: int, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Просмотр переписки по user_id
    """

    messages = db.query(Message).filter(
        ((Message.sender_id == user.id) & (Message.accepted_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.accepted_id == user.id))
    ).order_by(Message.created_at).all()

    if messages:

        sender_id = message.sender_id
        accepted_id = message.accepted_id
        key_sender_from_json = load_private_key_from_file(sender_id)
        key_accepted_from_json = load_private_key_from_file(accepted_id)

        # Делаем из них объекты криптографии
        private_key_sender = load_private_key_from_data(key_sender_from_json)
        private_key_accepted = load_private_key_from_data(key_accepted_from_json)

        # Выводим по времени отправленных сообщений
        message_object = db.query(Message).order_by(asc(Message.created_at)).all()
        message_dict = []
        for message in message_object:
            sender = message.sender  # Объект отправителя User
            accepted = message.accepted  # Объект кто принял User
            b_message = byte_string(message.text)

            # Определяем, какой ключ использовать на основе отправителя и получателя
            if user.id == sender_id:
                private_key = private_key_sender
            elif user.id == accepted_id:
                private_key = private_key_accepted
            else:
                raise HTTPException(status_code=403, detail="Недостаточно прав для доступа к сообщению")

            print(private_key)
            print(b_message)


            # Расшифровываем сообщение
            #message_result = decrypt_test(b_message, private_key)
            #message_result_str = message_result.decode('utf-8')

            message_info = {
                "id_message": message.id,
                "sender": sender.name,
                "text": message.text,
                "accepted": accepted.name,
                "created_at": str(message.created_at),
                "status": message.status
            }
            message_dict.append(message_info)

        return message_dict
    else:
        raise HTTPException(status_code=404, detail="Диалог не найден")


# 31         eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MzF9.3iKpsR9sImFQXCnoVLsbUfk5c5ViRx-maD7V-7KjWPQ
# 32         eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MzJ9.qZwWCacW5pL9JAGx6uvZ6iz0oEUg_hTBJcW_LTkBIbA

@router.get('/test/{message_id}', summary='SendMessage', response_model=dict)
def message_view(message_id: int, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Тест расшифровки сообщение по его айди
    """
    message_object = db.query(Message).filter(Message.id == message_id).first()

    if message_object:
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




# # Получаем из json файла приватный ключ
# key_from_json = load_private_key_from_file(sender.id)
# # Делаем из него объект криптографии
# key = load_private_key_from_data(key_from_json)

# @router.get('/{message_id}', summary='SendMessage', response_model=list[MessageView])
# def message_view(message_id: int, user: User = Depends(get_user), db: Session = Depends(get_db)):
#     """
#     Просмотр переписки по message_id
#     """
#     message_all = db.query(Message).filter(Message.id == message_id).all()
#
#     # Проверка что он один из переписки
#     message_object = db.query(Message).filter(
#         or_(Message.accepted_id == user.id, Message.sender_id == user.id)
#     ).first()
#
#     if message_all and message_object:
#         # Выводим по времени отправленных сообщений
#         message_object = db.query(Message).order_by(asc(Message.created_at)).all()
#         message_dict = []
#         for message in message_object:
#             sender = message.sender  # Объект отправителя User
#             accepted = message.accepted  # Объект кто принял User
#
#             decrypt_message = decrypt_caesar(message.text, message.key)  # Расшифровка сообщение
#             message_info = {
#                 "id_message": message.id,
#                 "sender": sender.name,
#                 "text": decrypt_message,
#                 "accepted": accepted.name,
#                 "created_at": str(message.created_at),
#                 "status": message.status
#             }
#             message_dict.append(message_info)
#
#         return message_dict
#
#     else:
#         raise HTTPException(status_code=404, detail="Диалог не найден")


@router.delete('/{message_id}', summary='SendMessage', response_model=dict)
def message_one_delete(message_id: int, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Удалить сообщение у твоих
    """
    # Проверка что он один из переписки
    message_object = db.query(Message).filter(
        or_(Message.accepted_id == user.id, Message.sender_id == user.id)
    ).first()
    if message_object:
        delete_message = db.query(Message).filter(Message.id == message_id).first()
        db.delete(delete_message)
        db.commit()
        return {"message": "Сообщение успешно удалено"}
    else:
        raise HTTPException(status_code=401, detail="Нет прав доступа")
