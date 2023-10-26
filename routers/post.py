from fastapi import APIRouter, Depends
from base.database import get_db
from sqlalchemy.orm import Session
from base.models import Post, User, Comment
from base.schemas import CreatePost, ViewPost
from authentication.security import get_user

router = APIRouter()


# http://127.0.0.1:8000/api/v1/social-network/user/post/create
@router.post('/create', summary='CreatePost', response_model=dict)
def create_post(post: CreatePost, user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    POST
    Создание поста
    """
    new_post = Post(text=post.text, user_id=user.id)
    db.add(new_post)
    db.commit()
    return {"message": "Пост успешно создан"}


# http://127.0.0.1:8000/api/v1/social-network/user/post/mypost
@router.get('/mypost', summary='ViewUserPost', response_model=list[ViewPost])
def view_user_post(user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    GET
    Получить все посты пользователя
    """
    user_posts = db.query(Post).filter(Post.user_id == user.id).all()
    if user_posts:
        posts_as_dicts = [
            {
                "id": post.id,
                "text": post.text,
                "created_at": str(post.created_at),
                "user_id": post.user_id,
            }
            for post in user_posts
        ]

        return posts_as_dicts
    else:
        return []


#http://127.0.0.1:8000/api/v1/social-network/user/post/{post_id}/comments/view
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
                "text": comment.text,
                "created_at": comment.created_at,
                "user_id": comment.user_id
            }
            for comment in comments
        ]
        return comment_list
    else:
        return []



#http://127.0.0.1:8000/api/v1/social-network/user/post/{user_id}/view
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


