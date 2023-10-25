from fastapi import APIRouter, HTTPException, Depends, Header
from authentication.security import decoded_token
from base.models import User
from base.schemas import UserProfile
from base.database import get_db
from sqlalchemy.orm import Session


router = APIRouter()


@router.get('/profile', summary="ProfileUser", response_model=UserProfile)
def profile_user_jwt(authorization: str = Header(...), db: Session = Depends(get_db)):
    """
    GET
    Профиль пользователя
    """
    return decoded_token(authorization, db)
