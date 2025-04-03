# FastAPI Audio Upload API

Проект представляет собой API-сервис на FastAPI для загрузки и хранения аудиофайлов с авторизацией через Яндекс OAuth. Поддерживается роль суперпользователя с расширенными правами.

---

## Быстрый старт

### 1. Клонируйте репозиторий

```
git clone https://github.com/MihaelTsvetkov/FastApiAudioTestTask.git
cd your--app
```

установите зависимости из requirements.txt

### 2. Создайте .env файл
```
POSTGRES_HOST=хост базы
POSTGRES_PORT=порт базы
POSTGRES_DB=имя базы
POSTGRES_USER=пользователь
POSTGRES_PASSWORD=пароль

YANDEX_CLIENT_ID=ваш_client_id
YANDEX_CLIENT_SECRET=ваш_client_secret
```

### 3. Соберите и запустите проект
```
docker-compose up --build
```

### После запуска:

документация будет доступна по адресу: http://localhost:8000/docs


### Конфигурация

Основная конфигурация берётся из .env и используется в приложении по умолчанию.

Для тестов — переопределяется переменная DATABASE_URL (обычно localhost:5433 или отдельная БД test_db).

Все тесты используют изолированную конфигурацию и не влияют на основную БД.


### Авторизация через Яндекс

1. Перейдите по http://localhost:8000/login

2. После перехода на страницу ПОДОЖДИТЕ 3–5 секунд, прежде чем нажимать кнопку.

3. Введите данные Яндекса.

4. Вы будете перенаправлены обратно с токеном доступа.

5. Скопируйте access и refresh токен 

После этого можно выполнять защищённые запросы. Токен указывается в заголовке Authorization: Bearer <your_token>


### Пользовательские эндпоинты

### GET /files

Получить список всех файлов текущего пользователя.

Требует авторизации

Ответ: список файлов (ID, имя, время загрузки, путь)

```
[
  {
        "filename": "sample.mp3",
        "id": "0ceab514-c6cb-4d2f-9c3d-251e6ee2256d",
        "stored_path": "media/0ceab514-c6cb-4d2f-9c3d-251e6ee2256d.mp3",
        "uploaded_at": "2025-04-02T22:29:40.634344"
    }
]
```


### POST /files/upload

Загрузка аудиофайла (формы .mp3, .wav, .ogg).

Требует авторизации

Формы:

filename: строка (имя файла)

file: файл

Ответ: загруженный файл

```
{
    "filename": "sample.mp3",
    "id": "4313fafe-258d-4a0c-afd5-f811bccb6478",
    "stored_path": "media/4313fafe-258d-4a0c-afd5-f811bccb6478.mp3",
    "uploaded_at": "2025-04-02T22:46:06.105316"
}
```


### POST /auth/refresh
Получение новго access токена

Требует refresh токен

пример json тела
```
{
  "refresh_token": "ваш refresh токен"

}
```

Ответ: новый access токен

```
{
    "access_token": "access_token"
    "token_type": "bearer"
}
```

### Ключ суперпользователя

После запуска контейнера в терминале появится лог:

```
SUPERUSER ACCESS TOKEN: <superuser_api_key>
```

Скопируйте его — это ключ доступа к эндпоинтам суперпользователя.

**Он не выводится повторно, поэтому сохраните сразу!**


### Эндпоинты суперпользователя

Все запросы выполняются с заголовком:
```
Authorization: Bearer <superuser_api_key>
```


### GET /admin/users

Получить список всех пользователей системы.

Только для суперпользователя

Ответ: список пользователей с ID, email и датой регистрации

```
[
    {
        "email": "admin@example.com",
        "id": "704f4db6-9453-4cd0-97c3-5dd22c3b6dab",
        "is_superuser": true,
        "created_at": "2025-04-02T22:25:54.991771Z"
    },
    {
        "email": "wiiliamblake@yandex.ru",
        "id": "23605230-b34e-4f91-8e40-724e3bf3da41",
        "is_superuser": false,
        "created_at": "2025-04-02T22:27:04.471339Z"
    }
]
```

### GET /admin/users{user_id}

Получить пользователя по его id.

Только для суперпользователя

Ответ: Пользователь с указанным id

```
{
    "email": "wiiliamblake@yandex.ru",
    "id": "23605230-b34e-4f91-8e40-724e3bf3da41",
    "is_superuser": false,
    "created_at": "2025-04-02T22:27:04.471339Z"
}
```

### PATCH /admin/patch/{user_id}

Изменить данные о пользователе (почта, is_superuser) по его ID.

 Только для суперпользователя

пример json body: 

```
{
    "email": "newemail@example.com",
}
```

Ответ: Пользователь с новыми данными

```
{
    "email": "newemail@example.com",
    "id": "23605230-b34e-4f91-8e40-724e3bf3da41",
    "is_superuser": false,
    "created_at": "2025-04-02T22:27:04.471339Z"
}
```
