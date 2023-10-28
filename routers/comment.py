from fastapi import APIRouter, Depends, HTTPException
from base.database import get_db
from sqlalchemy.orm import Session
from base.models import Comment, User, Post
from base.schemas import CreateCommentPost, ChangeComment
from authentication.security import get_user

router = APIRouter()


# http://127.0.0.1:8000/api/v1/social-network/user/post/{post_id}/comment/create
@router.post('/create', summary='CreateCommentPost', response_model=dict)
def create_comment_post(post_id: int, comment: CreateCommentPost, user: User = Depends(get_user),
                        db: Session = Depends(get_db)):
    """
    Создание комментария к посту по post_id
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        new_comment_post = Comment(text=comment.text, user_id=user.id, post_id=post_id)
        db.add(new_comment_post)
        db.commit()
        return {"message": "Комментарий успешно создан"}
    else:
        raise HTTPException(status_code=404, detail="Поста с таким id не найден")

#http://127.0.0.1:8000/api/v1/social-network/user/post/{post_id}/comment/change-comment/{comment_id}
@router.put('/change-comment/{comment_id}', summary='ChangeTextComment', response_model=dict)
def change_comment_text(post_id: int, comment_id: int, text: ChangeComment, user: User = Depends(get_user),
                        db: Session = Depends(get_db)):
    """
    Редактирование текст комментария к посту по post_id и comment_id
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        if comment.user_id == user.id:
            comment.text = text.new_text
            db.commit()
            return {"message": "Текст комментария успешно изменен"}
        else:
            raise HTTPException(status_code=403, detail="Нет прав доступа")
    else:
        raise HTTPException(status_code=404, detail="Комментарий не найден")


#http://127.0.0.1:8000/api/v1/social-network/user/post/{post_id}/comment/delete-comment/{comment_id}
@router.delete('/delete-comment/{comment_id}', summary='ChangeTextComment', response_model=dict)
def change_comment_text(post_id: int, comment_id: int, text: ChangeComment, user: User = Depends(get_user),
                        db: Session = Depends(get_db)):
    """
    Удаление комментария к посту по post_id и comment_id
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        if comment.user_id == user.id or user.status == 'admin':
            db.delete(comment)
            db.commit()
            return {"message": "Комментарий успешно удален"}
        else:
            raise HTTPException(status_code=403, detail="Нет прав доступа")
    else:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
