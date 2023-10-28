from fastapi import APIRouter, HTTPException, Depends
from authentication.security import create_jwt_token, hash_object, check_password, SECRET_KEY_JWT
from base.models import User
from base.schemas import RegisterUser, LoginUser
from base.database import get_db
from sqlalchemy.orm import Session
from email_validator import validate_email, EmailNotValidError

router = APIRouter()


# http://127.0.0.1:8000/api/v1/social-network/auth/register
@router.post('/register', summary='RegisterUser', response_model=dict)
def create_user(user: RegisterUser, db: Session = Depends(get_db)):
    """
    Регистрация пользователя
    """
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Длина пароля должна быть больше 6 символов")

    # Проверка почты на валидность
    try:
        validate_email(user.mail)
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail="Некорректный формат email-адреса")

    # Хешируем пароль
    hashed_password = hash_object(user.password)
    hashed_password_str = hashed_password.decode("utf-8")

    # Создаем объект базы и сохраняем хеш пароля в виде строки
    # Без decode("utf-8") он сохраняется с потерей salt
    user_object = User(name=user.name, surname=user.surname, mail=user.mail, password=hashed_password_str)

    db.add(user_object)
    db.commit()
    response_data = {"message": "Пользователь успешно зарегистрирован"}
    return response_data


# http://127.0.0.1:8000/api/v1/social-network/auth/login
@router.post('/login', summary='LoginUser', response_model=dict)
def login_user(user: LoginUser, db: Session = Depends(get_db)):
    """
    Авторизация пользователя по почте и паролю
    и получение токена JWT
    """
    match_user_mail = db.query(User).filter(User.mail == user.mail).first()

    if match_user_mail is None:
        raise HTTPException(status_code=400, detail="Неверная почта")

    if check_password(user.password, match_user_mail.password):
        user_data = {"id": match_user_mail.id}
        token = create_jwt_token(user_data, SECRET_KEY_JWT)

        response_data = {
            "message": "Авторизация успешна",
            "token": token,
            "description": "Используйте этот JWT токен для доступа к профилю"
        }

        return response_data
    else:
        raise HTTPException(status_code=400, detail="Неверный пароль")
