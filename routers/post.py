from fastapi import APIRouter, Depends, HTTPException
from base.database import get_db
from sqlalchemy.orm import Session
from base.models import Post, User, Comment, Reaction
from base.schemas import CreatePost, ViewPost, ChangePost
from authentication.security import get_user


router = APIRouter()


# http://127.0.0.1:8000/api/v1/social-network/user/post/create
@router.post('/create', summary='CreatePost', response_model=dict)
def create_post(post: CreatePost, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    POST
    Создание поста с текстом
    """
    new_post = Post(text=post.text, user_id=user.id)
    db.add(new_post)
    db.commit()
    return {"message": "Пост успешно создан"}


@router.put('/change-post/{post_id}', summary='ChangeTextPost', response_model=dict)
def change_post_text(post_id: int, text: ChangePost, user: User = Depends(get_user),
                     db: Session = Depends(get_db)):
    """
    PUT
    Редактирование текст поста по post_id
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        if post.user_id == user.id:
            post.text = text.new_text
            db.commit()
            return {"message": "Текст поста успешно изменен"}
        else:
            raise HTTPException(status_code=403, detail="Нет прав доступа")
    else:
        raise HTTPException(status_code=404, detail="Пост не найден")


@router.delete('/delete-post/{post_id}', summary='DeletePost', response_model=dict)
def delete_post(post_id: int, user: User = Depends(get_user),
                db: Session = Depends(get_db)):
    """
    Удаление поста по post_id
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        if post.user_id == user.id:
            db.delete(post)
            db.commit()
            return {"message": "Пост успешно удален"}
        else:
            raise HTTPException(status_code=403, detail="Нет прав доступа")
    else:
        raise HTTPException(status_code=404, detail="Пост не найден")


# http://127.0.0.1:8000/api/v1/social-network/user/post/mypost
@router.get('/mypost', summary='ViewUserPost', response_model=list[ViewPost])
def view_user_post(user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Получить все посты пользователя с указанием количества лайков
    и информацией о том, кто поставил лайк
    """
    user_posts = db.query(Post).filter(Post.user_id == user.id).all()

    if user_posts:
        posts_as_dicts = []
        for post in user_posts:
            likes = db.query(Reaction).filter(Reaction.post_id == post.id).all()
            likes_info = []
            for like in likes:
                user_who_liked = db.query(User).filter(User.id == like.user_id).first()
                likes_info.append({
                    "user_id": user_who_liked.id,
                    "user_name": user_who_liked.name,
                    "user_surname": user_who_liked.surname
                })

            posts_as_dicts.append({
                "id": post.id,
                "text": post.text,
                "created_at": str(post.created_at),
                "like_count": post.like_count,
                "user_id": post.user_id,
                "likes": likes_info
            })

        return posts_as_dicts
    else:
        return []


# http://127.0.0.1:8000/api/v1/social-network/user/post/{post_id}/comments/view
@router.get('/{post_id}/comments/view', summary='ViewCommentPost', response_model=list[dict])
def view_post_comment(post_id: int, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    GET
    Просмотр комментариев поста по id поста
    """
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    if comments:
        comment_list = [
            {
                "id": comment.id,
                "text": comment.text,
                "created_at": comment.created_at,
                "user_id": comment.user_id
            }
            for comment in comments
        ]
        return comment_list
    else:
        return []


# http://127.0.0.1:8000/api/v1/social-network/user/post/{user_id}/view
@router.get('/{user_id}/view', summary='UserPostID', response_model=list[dict])
def user_post_id(user_id: int, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    GET
    Просмотр поста по id пользователя
    """
    posts = db.query(Post).filter(Post.user_id == user_id).all()

    if posts:
        posts_list = [
            {
                "id": post.id,
                "text": post.text,
                "created_at": str(post.created_at),
                "user_id": post.user_id
            }
            for post in posts
        ]
        return posts_list
    else:
        return []
