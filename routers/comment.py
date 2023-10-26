from fastapi import APIRouter, Depends, Header
from base.database import get_db
from sqlalchemy.orm import Session
from base.models import Comment
from base.schemas import CreateCommentPost
from authentication.security import decoded_token

router = APIRouter()


# http://127.0.0.1:8000/api/v1/social-network/user/post/{post_id}}/comment/create
@router.post('/create', summary='CreateCommentPost', response_model=dict)
def create_comment_post(post_id: int, comment: CreateCommentPost, authorization: str = Header(...),
                        db: Session = Depends(get_db)):
    """
    POST
    Создание комментария по id поста
    """
    user_object = decoded_token(authorization, db)
    if user_object:
        new_comment_post = Comment(text=comment.text, user_id=user_object.id, post_id=post_id)
        db.add(new_comment_post)
        db.commit()
        return {"message": "Комментарий успешно создан"}
