from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import asc, or_
import random
from base.database import get_db
from sqlalchemy.orm import Session
from base.models import User, Message
from base.schemas import MessageView
from authentication.security import get_user, encrypt_caesar, decrypt_caesar, hash_object
from base.schemas import SendMessage

router = APIRouter()


# http://127.0.0.1:8000/api/v1/social-network/user/message/{user_id}/send
@router.post('/{user_id}/send', summary='SendMessage', response_model=dict)
def send_message(user_id: int, message: SendMessage, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Отправка сообщение по user_id
    """
    accepted_user = db.query(User).filter(User.id == user_id)

    if accepted_user:
        # Рандомный ключ шифрования
        random_number = random.randint(1, 100)
        print(random_number)
        # Шифруем текст
        encrypt_message = encrypt_caesar(message.text, random_number)
        new_message = Message(sender_id=user.id, accepted_id=user_id, text=encrypt_message, key=random_number)
        print(new_message.key)
        db.add(new_message)
        db.commit()
        return {"message": "Сообщение успешно отправлено"}
    raise HTTPException(status_code=404, detail="Пользователь не найден")


# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6OX0.n5GIoCjWNhFSWVtdq0bcnmEYL04eumsvJ0nYFGpFc_E                  ПЕРВЫЙ 9


# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTB9.9cEpUGmXiaa5-cix_C88bwwnkbgpu6jM1OgVsebAqto        ВТОРОЙ 10


# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTN9.pBmszR1cRjE7n_PXmq7KYQ8jJICLJRDLjzRwqROnEkU      Левый тип
@router.get('/{message_id}', summary='SendMessage', response_model=list[MessageView])
def message_view(message_id: int, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Просмотр переписки по message_id
    """
    message_all = db.query(Message).filter(Message.id == message_id).all()

    # Проверка что он один из переписки
    message_object = db.query(Message).filter(
        or_(Message.accepted_id == user.id, Message.sender_id == user.id)
    ).first()

    if message_all and message_object:
        # Выводим по времени отправленных сообщений
        message_object = db.query(Message).order_by(asc(Message.created_at)).all()
        message_dict = []
        for message in message_object:
            sender = message.sender  # Объект отправителя User
            accepted = message.accepted  # Объект кто принял User

            decrypt_message = decrypt_caesar(message.text, message.key)  # Расшифровка сообщение
            message_info = {
                "id_message": message.id,
                "sender": sender.name,
                "text": decrypt_message,
                "accepted": accepted.name,
                "created_at": str(message.created_at),
                "status": message.status
            }
            message_dict.append(message_info)

        return message_dict

    else:
        raise HTTPException(status_code=404, detail="Диалог не найден")


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
