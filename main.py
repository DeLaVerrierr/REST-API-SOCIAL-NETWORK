from fastapi import FastAPI
from routers import auth, post, friend, user

app = FastAPI()

app.include_router(auth.router, prefix="/api/v1/social-network/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/api/v1/social-network/user", tags=["User"])
app.include_router(post.router, prefix="/api/v1/social-network/post", tags=["Post"])
app.include_router(friend.router, prefix="/api/v1/social-network/friend", tags=["Friends"])