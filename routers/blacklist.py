from fastapi import APIRouter, Depends, HTTPException
from base.database import get_db
from sqlalchemy.orm import Session
from base.models import User, Blacklist
from authentication.security import get_user
from base.schemas import ViewBlacklist

router = APIRouter()


# http://127.0.0.1:8000/api/v1/social-network/user/blacklist/{user_id}/add
@router.post('/{user_id}/add', summary='AddBlacklist', response_model=dict)
def add_user_blacklist(user_id: int, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Добавление пользователя по id в черный список
    """
    add_user = db.query(User).filter(User.id == user_id).first()
    # Проверка на то чтобы user_id не совпадал с id того кто обратился к точке
    if user_id == user.id:
        raise HTTPException(status_code=403, detail="Нельзя добавить себя в черный список")

    if add_user:
        new_blacklist = Blacklist(who_added=user.id, who_was_added=user_id)
        db.add(new_blacklist)
        db.commit()
        return {"message": "Пользователь добавлен в черный список"}

    raise HTTPException(status_code=404, detail="Пользователь не найден")


# http://127.0.0.1:8000/api/v1/social-network/user/blacklist/{user_id}/remove

@router.delete('/{user_id}/delete', summary='DeleteBlacklist', response_model=dict)
def delete_user_from_blacklist(user_id: int, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Удаление пользователя по id из черного списка
    """
    user_form_blacklist = db.query(Blacklist).filter(
        Blacklist.who_added == user.id and Blacklist.who_was_added == user_id).first()

    if user_form_blacklist:
        db.delete(user_form_blacklist)
        db.commit()
        return {"message": "Пользователь удален из черного списка"}

    raise HTTPException(status_code=404, detail="Пользователь не найден")


@router.get('/view', summary='ViewBlacklist', response_model=list[ViewBlacklist])
def user_blacklist(user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Просмотра черного списка пользователя
    """

    blacklist = db.query(Blacklist).filter(Blacklist.who_added == user.id).all()
    if blacklist:
        blacklist_dicts = []
        for user in blacklist:
            # Объект пользователя кто в списке, чтобы вывести его имя
            user_object = db.query(User).filter(User.id == user.who_was_added).first()

            blacklist_dicts.append({
                "user_id": user.who_was_added,
                "name": user_object.name,
                "surname": user_object.surname
            })
        return blacklist_dicts
    else:
        return []

# Vova eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NX0.2Q5uIXovToOV0kIm2TDwfkn3vD8IxBIyqtnjwPiS5pw
# TESTB eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Nn0.PGURZbQ1WQr8edtgYxCLWPfi5sB6h5bPj2D4FOoH_UA
