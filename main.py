from fastapi import FastAPI
from routers import auth, post, friend, user, comment

app = FastAPI()

app.include_router(auth.router, prefix="/api/v1/social-network/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/api/v1/social-network/user", tags=["User"])
app.include_router(post.router, prefix="/api/v1/social-network/user/post", tags=["Post"])
app.include_router(comment.router, prefix="/api/v1/social-network/user/post/{post_id}/comment", tags=["Comment"])
app.include_router(friend.router, prefix="/api/v1/social-network/user/friend", tags=["Friends"])