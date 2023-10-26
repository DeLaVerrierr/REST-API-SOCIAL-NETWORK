from fastapi import APIRouter, Depends
from authentication.security import get_user
from base.models import User, Friend
from base.schemas import UserProfile
from base.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
router = APIRouter()


# http://127.0.0.1:8000/api/v1/social-network/user/profile
@router.get('/profile', summary="ProfileUser", response_model=UserProfile)
def profile_user_jwt(user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    GET
    Профиль пользователя
    """

    friend_requests_received = db.query(Friend).filter(Friend.second_user_id == user.id).all()

    friend_requests_sent = db.query(Friend).filter(Friend.first_user_id == user.id).all()

    friend_list = []
    for friend in friend_requests_received:
        friend_list.append({
            "id_user": friend.first_user_id
        })
    for friend in friend_requests_sent:
        friend_list.append({
            "id_user": friend.second_user_id
        })

    return UserProfile(
        name=user.name,
        surname=user.surname,
        mail=user.mail,
        friends=friend_list
    )

#http://127.0.0.1:8000/api/v1/social-network/user/delete-friend/{friend_id}
@router.post('/delete-friend/{friend_id}', summary="DeleteFriend", response_model=dict)
def profile_user_jwt(friend_id: int, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    POST
    Удалить пользователя из друзей
    """
    friend = db.query(Friend).filter(
        or_(
            and_(Friend.first_user_id == user.id, Friend.second_user_id == friend_id),
            and_(Friend.first_user_id == friend_id, Friend.second_user_id == user.id)
        )
    ).first()

    if friend:
        db.delete(friend)
        db.commit()
        return {"message": "Друг успешно удален"}
    else:
        return {"message": "Друг не найден"}
