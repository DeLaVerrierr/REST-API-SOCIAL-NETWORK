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
    - Смена пароля
2. **Посты:**
    - Создание, редактирование, удаление постов с текстом
    - Просмотр постов других пользователей и своих
3. **Комментарии к постам:**
    - Добавление, редактирование, удаление комментариев к постам
    - Просмотр комментариев 
4. **Реакции к постам:**
    - Возможность лайкнуть пост 
5. **Дружба:**
    - Отправление запроса на дружбу
    - Отклонение или принятие запроса 
    - Просмотр заявок на дружбу
    - Просмотра списка друзей в профиле пользователя
    - Удаление пользователя из друзей
6. **Лента:**
    - Просмотр всех постов с приоритетом на количество лайков
7. **Сообщения:**
    - Отправка сообщение пользователям
    - Просмотр диалога 
    - Удаление сообщение 

## Требования к безопасности:

1. Защита от SQL-инъекций. Выполнена простая защита с использованием встроенной ORM SQLAlchemy.
2. Хранение паролей пользователей в безопасной форме (хеширование) с использованием библиотеки `bcrypt`
3. Использование токенов JWT для аутентификации.
4. Шифрование сообщений через RSA. Публичные ключи сохраняются в базе с User, а приватные ключи сохраняются в PEM формате json файле. Подробнее про технологию RSA 
![rsa.jpg](img_readme%2Frsa.jpg)

## Тестирование:
1. 

## Документация:
1. /docs/ автогенерация через Swagger
