from typing import List
from fastapi import APIRouter, Depends, HTTPException
from base.database import get_db
from sqlalchemy.orm import Session
from base.models import User, Message, Blacklist
from base.schemas import MessageResponse, SendMessage
from authentication.security import get_user, load_private_key_from_file
import rsa


router = APIRouter()


# http://127.0.0.1:8000/api/v1/social-network/user/message/{user_id}/send
@router.post('/{user_id}/send', summary='SendMessage', response_model=dict)
def send_message(user_id: int, message: SendMessage, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Отправка сообщение по user_id
    """
    accepted_user = db.query(User).filter(User.id == user_id).first()

    blacklist = db.query(Blacklist).filter(Blacklist.who_added == user_id and Blacklist.who_was_added == user.id).first()
    # Проверка есть ли он в черном списке
    if blacklist:
        raise HTTPException(status_code=403, detail="Вы в черном списке")

    if accepted_user:
        # Делаем из строки в объект публичный ключ
        loaded_pubkey = rsa.PublicKey.load_pkcs1(user.public_key.encode())
        # Из строки делаеем байты
        message = str.encode(message.text)
        # Зашифровываем сообщение передавая аргументы сообщение и публичный ключ как объект
        crypto_message = rsa.encrypt(message, loaded_pubkey)

        new_message = Message(sender_id=user.id, accepted_id=user_id, text=crypto_message)
        db.add(new_message)
        db.commit()

        return {"message": "Сообщение успешно отправлено"}
    raise HTTPException(status_code=404, detail="Пользователь не найден")


@router.get('/{user_id}', summary='ViewMessage', response_model=List[MessageResponse])
def correspondence(user_id: int, user: User = Depends(get_user), db: Session = Depends(get_db)):
    correspondence = db.query(Message).filter(
        ((Message.sender_id == user.id) & (Message.accepted_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.accepted_id == user.id))
    ).all()

    if not correspondence:
        raise HTTPException(status_code=404, detail="Диалог не найден")

    response_messages = []

    for message in correspondence:
        # Вытаскиваем приватный ключ из json файла по id отправителя
        private_key = load_private_key_from_file(message.sender_id)
        # Из str делаем приватный ключ в объект
        loaded_privkey = rsa.PrivateKey.load_pkcs1(private_key.encode())
        # Убираем /x из зашифрованного текста
        hex_string = message.text.replace("\\x", "").replace(" ", "")
        # Делаем из него байты
        byte_string = bytes.fromhex(hex_string)
        # Расшифровываем передавая аргументы текст в байты и приватный ключ как объект
        message_text = rsa.decrypt(byte_string, loaded_privkey)

        sender_name = message.sender.name
        accepted_name = message.accepted.name

        response_message = {
            "id": message.id,
            "sender_name": sender_name,
            "accepted_name": accepted_name,
            "text": message_text,
            "created_at": str(message.created_at),
            "status": message.status
        }
        response_messages.append(response_message)

    return response_messages


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

        return {'message': message}


@router.delete('/{user_id}/{message_id}', summary='SendMessage', response_model=dict)
def message_one_delete(user_id: int, message_id: int, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Удалить сообщение у двоих
    """
    # Для доступа к конечной точке пользователь должен быть отправителем сообщения, а другой участник переписки
    # должен быть принимающим сообщение

    correspondence = db.query(Message).filter(
        (
                (Message.sender_id == user.id) & (Message.accepted_id == user_id)
        )
    ).filter(Message.id == message_id).first()

    if correspondence:
        db.delete(correspondence)
        db.commit()
        return {"message": "Сообщение успешно удалено"}
    else:
        raise HTTPException(status_code=401, detail="Нет прав доступа")

