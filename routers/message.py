import binascii
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import asc, or_
import random
from base.database import get_db
from sqlalchemy.orm import Session
from base.models import User, Message
from base.schemas import MessageView
from authentication.security import get_user, load_private_key_from_file
import rsa

from base.schemas import SendMessage

router = APIRouter()


# http://127.0.0.1:8000/api/v1/social-network/user/message/{user_id}/send
@router.post('/{user_id}/send', summary='SendMessage', response_model=dict)
def send_message(user_id: int, message: SendMessage, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Отправка сообщение по user_id
    """
    accepted_user = db.query(User).filter(User.id == user_id).first()

    if accepted_user:
        loaded_pubkey = rsa.PublicKey.load_pkcs1(user.public_key.encode())
        message = str.encode(message.text)
        crypto_message = rsa.encrypt(message, loaded_pubkey)

        new_message = Message(sender_id=user.id, accepted_id=user_id, text=crypto_message)
        db.add(new_message)
        db.commit()

        return {"message": "Сообщение успешно отправлено"}
    raise HTTPException(status_code=404, detail="Пользователь не найден")



@router.get('/test/{message_id}', summary='SendMessage', response_model=dict)
def message_view(message_id: int, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Тест расшифровки сообщение по его id
    """


    message_object = db.query(Message).filter(Message.id == message_id).first()

    if message_object:
        # Вытаскиваем приватный ключ из json файла по id кто отправил сообщение
        private_key = load_private_key_from_file(message_object.sender_id)
        print(f'Вытащили ключ вот такой {private_key}')
        # Преобразовываем его в формат PrivateKey
        loaded_privkey = rsa.PrivateKey.load_pkcs1(private_key.encode())
        print(f'Превратиили ключ в объект {loaded_privkey}')
        # Из зашифрованного сообщение убираем \x
        hex_string = message_object.text.replace("\\x", "").replace(" ", "")

        # Преобразуем шестнадцатеричную строку в байты
        byte_string = bytes.fromhex(hex_string)
        # Разшифровываем текст
        message = rsa.decrypt(byte_string, loaded_privkey)

        return {'message':message}





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
