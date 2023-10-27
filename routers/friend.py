from fastapi import APIRouter, Depends,HTTPException
from base.database import get_db
from sqlalchemy.orm import Session
from base.models import User, RequestFriend, Friend
from authentication.security import get_user

router = APIRouter()


# first_user_id тот кто отрпавил заявку
# second_user_id тот кому пришла заявка


# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6OX0.n5GIoCjWNhFSWVtdq0bcnmEYL04eumsvJ0nYFGpFc_E                  ПЕРВЫЙ 9


# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTB9.9cEpUGmXiaa5-cix_C88bwwnkbgpu6jM1OgVsebAqto        ВТОРОЙ 10


# http://127.0.0.1:8000/api/v1/social-network/user/friend/friend-requests/{user_id}
@router.post('/friend-requests/{user_id}', summary='RequestsFriend', response_model=dict)
def friend_requests(user_id: int, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Отправка запроса на дружбу по user_id
    """
    if user_id == user.id:
        raise HTTPException(status_code=403, detail="Нельзя отправлять заявку в друзья самому себе")

    request_new = RequestFriend(first_user_id=user.id, second_user_id=user_id)
    db.add(request_new)
    db.commit()
    return {"message": "Заявка на добавление в друзья отправлена"}


# http://127.0.0.1:8000/api/v1/social-network/user/friend/friend-requests/{request_id}/accept
@router.post('/friend-requests/{request_id}/accept', summary='AcceptFriend', response_model=dict)
def accept_requests_friend(request_id: int, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Принятие предложение дружбы по request_id
    """
    request_friend = db.query(RequestFriend).filter(RequestFriend.id == request_id).first()
    if request_friend:
        new_friend = Friend(first_user_id=request_friend.first_user_id, second_user_id=request_friend.second_user_id)
        db.add(new_friend)
        db.delete(request_friend)
        db.commit()
        return {"message": "Вы приняли предложение о дружбе"}
    else:
        raise HTTPException(status_code=404, detail="Заявка не найдена")


# http://127.0.0.1:8000/api/v1/social-network/user/friend/friend-requests/{request_id}/reject
@router.post('/friend-requests/{request_id}/reject', summary='RejectFriend', response_model=dict)
def accept_requests_friend(request_id: int, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Отклонение предложение дружбы по request_id
    """
    request_friend = db.query(RequestFriend).filter(RequestFriend.id == request_id).first()
    if request_friend:
        db.delete(request_friend)
        db.commit()
        return {"message": "Вы отклонили предложение о дружбе"}
    else:
        raise HTTPException(status_code=404, detail="Заявка не найдена")



# http://127.0.0.1:8000/api/v1/social-network/user/friend/friend-requests/received
@router.get('/friend-requests/received', summary='ViewFriendRequests', response_model=list[dict])
def view_received_friend_requests(user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Просмотр полученных запросов на дружбу
    """
    request_friend = db.query(RequestFriend).filter(RequestFriend.second_user_id == user.id).all()
    if request_friend:
        request_list = [
            {
                "request_id": request.id,
                "user_id": request.first_user_id,
                "createt_at": str(request.created_at)
            }
            for request in request_friend
        ]
        return request_list
    else:
        return []
