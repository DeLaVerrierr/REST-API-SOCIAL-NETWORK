##  Создание REST API для социальной сети

## Стэк:
 - Python
 - FastAPI
 - SQLAlchemy
 - PostgreSQL

## Функциональность
1. **Пользователи:**
    - Регистрация пользователей
    - Аутентификация пользователей по электронной почте и паролю, с последующей выдачей JWT-токена для доступа к профилю
2. **Посты:**
    - Создание постов с текстом
    - Просмотр постов других пользователей
3. **Комментарии к постам:**
    - Добавление комментариев к постам
    - Просмотр комментариев 
4. **Дружба:**
    - Отправление запроса на дружбу
    - Отклонение или принятие запроса 
    - Просмотра списка друзей в профиле пользователя
    - Удаление пользователя из друзей


## Требования к безопасности:

1. Защита от SQL-инъекций. Выполнена простая защита с использованием встроенной ORM SQLAlchemy.
2. Хранение паролей пользователей в безопасной форме (хеширование) с использованием библиотеки `bcrypt`
3. Использование токенов JWT для аутентификации.

## Тестирование:
1. 

## Документация:
1. /docs/ автогенерация через Swagger