from fastapi import APIRouter, Depends
from base.database import get_db
from sqlalchemy.orm import Session
from base.models import Post, User
from base.schemas import Feed
from authentication.security import get_user
from sqlalchemy import desc
router = APIRouter()


# http://127.0.0.1:8000/api/v1/social-network/feed
@router.get('', summary='FeedView', response_model=list[Feed])
def feed_view(user: User = Depends(get_user), db: Session = Depends(get_db)):
    """
    Лента постов
    """
    # Сортировка постов по количеству лайков
    posts = db.query(Post).order_by(desc(Post.like_count)).all()

    post_dicts = []
    for post in posts:
        post_dict = {
            "id": post.id,
            "text": post.text,
            "created_at": str(post.created_at),
            "user_id": post.user_id,
            "like_count": post.like_count,
        }
        post_dicts.append(post_dict)

    return post_dicts