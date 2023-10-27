from fastapi import APIRouter, Depends, HTTPException
from base.database import get_db
from sqlalchemy.orm import Session
from base.models import User, Post, Reaction

from authentication.security import get_user

router = APIRouter()


# http://127.0.0.1:8000/api/v1/social-network/user/post/{post_id}/reaction/like
@router.post('/like', summary='LikePost', response_model=dict)
def like_post(post_id: int, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Лайк поста
    При обращении еще раз лайк убирается
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        # Если лайк стоит, то лайк мы удаляем
        existing_like = db.query(Reaction).filter(Reaction.post_id == post_id, Reaction.user_id == user.id).first()
        if existing_like:
            db.delete(existing_like)
            post.like_count -= 1  # Убираем лайк
            db.commit()
            return {"message": "Лайк успешно удален"}

        like_post = Reaction(post_id=post_id, user_id=user.id)
        db.add(like_post)
        post.like_count += 1  # Добавляем лайк
        db.commit()
        return {"message": "Лайк успешно поставлен"}
    else:
        raise HTTPException(status_code=404, detail="Поста с таким id не найден")
