# Двухсервисная система LLM-консультаций

Проект представляет собой распределённую систему из двух независимых сервисов:

- **Auth Service** (FastAPI) – отвечает за регистрацию пользователей, аутентификацию и выпуск JWT-токенов.
- **Bot Service** (aiogram + Celery) – Telegram-бот, который принимает запросы к LLM и возвращает ответы, используя асинхронную обработку через очередь RabbitMQ и Redis.

## Архитектура и разделение обязанностей

- **Auth Service** хранит учётные данные пользователей в базе данных (SQLite), пароли хранятся в виде bcrypt-хешей. Сервис формирует JWT с полями `sub` (ID пользователя), `role`, `iat`, `exp`. Никакой логики Telegram-бота в Auth Service нет.
- **Bot Service** не занимается регистрацией и не хранит пароли. Он доверяет только JWT, выданный Auth Service. Токен передаётся боту командой `/token <jwt>`, сохраняется в Redis с привязкой к Telegram user_id и проверяется при каждом обращении.
- **LLM-запросы** выполняются асинхронно: бот публикует задачу в очередь RabbitMQ, Celery-воркер забирает её, обращается к OpenRouter API и отправляет ответ пользователю.
- **Redis** используется как кэш для хранения JWT (ключ `token:<tg_user_id>`) и как backend результатов Celery.
- **RabbitMQ** выступает брокером задач Celery, обеспечивая надёжную асинхронную обработку.

## Требования

- Python 3.11+
- Docker и Docker Compose (для RabbitMQ и Redis) или локально установленные RabbitMQ и Redis
- `uv` (или `pip`) для управления зависимостями
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))
- API-ключ [OpenRouter](https://openrouter.ai)

## Установка и настройка

1. Клонируйте репозиторий и перейдите в корневую папку.
2. Для каждого сервиса (`auth_service/` и `bot_service/`) выполните:
   ```bash
   uv sync

В каждом сервисе настройте файл .env:

JWT_SECRET – одинаковая секретная строка в обоих .env (сгенерируйте openssl rand -hex 32).
TELEGRAM_BOT_TOKEN – токен Telegram-бота (только в bot_service/.env).
OPENROUTER_API_KEY – API-ключ OpenRouter (только в bot_service/.env).
OPENROUTER_MODEL – модель, например stepfun/step-3.5-flash:free.

Для локального запуска RabbitMQ и Redis в Docker убедитесь, что переменные REDIS_URL и RABBITMQ_URL указывают на localhost (как в примере ниже), или измените их в соответствии с вашим окружением.

Пример bot_service/.env (для Docker на локальной машине):


REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672//

## Запуск
### 1. Инфраструктура (RabbitMQ, Redis)

Если используете Docker:
docker run -d --name redis -p 6379:6379 redis:7-alpine
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=guest -e RABBITMQ_DEFAULT_PASS=guest \
  rabbitmq:3.13-management

Или установите RabbitMQ и Redis локально и запустите их стандартным способом.

### 2. Auth Service

cd auth_service
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
Swagger-документация доступна по адресу http://localhost:8000/docs.

### 3. Celery Worker

cd bot_service
source .venv/bin/activate
celery -A app.infra.celery_app.celery_app worker --loglevel=info

### 4. Telegram-бот (aiogram polling)

cd bot_service
source .venv/bin/activate
python run_bot.py


## Пользовательский сценарий

### 1. Регистрация в Auth Service
Через Swagger (POST /auth/register) создайте пользователя с email вида `surname@email.com`.

![Запрос регистрации](screenshots/01_register_request.jpg)
![Ответ регистрации](screenshots/02_register_response.jpg)

### 2. Получение JWT
Выполните вход (POST /auth/login) с теми же учётными данными.

![Логин](screenshots/03_login.jpg)

Скопируйте значение `access_token`.

### 3. Передача токена боту
В Telegram отправьте боту команду `/token <ваш access_token>`.

![Отправка токена](screenshots/04_token_command.jpg)

Бот подтвердит принятие токена.

### 4. Запрос к LLM
Отправьте любой текстовый вопрос. Бот ответит «Запрос принят…» и через некоторое время вернёт ответ от LLM.

![Ответ бота](screenshots/05_llm_response.jpg)

### 5. Проверка профиля
Используя полученный токен, можно обратиться к GET /auth/me (через Swagger или curl).

![Профиль с токеном](screenshots/06_me_success.jpg)

Без токена эндпоинт возвращает 401.

![Профиль без токена](screenshots/07_me_unauthorized.jpg)

## Подтверждение работы очередей

В интерфейсе RabbitMQ ([http://localhost:15672](http://localhost:15672), логин/пароль `guest`) видны активные очереди Celery и подключения worker'а.

![Очереди RabbitMQ](screenshots/08_rabbitmq_queues.jpg)
![Подключения RabbitMQ](screenshots/09_rabbitmq_connections.jpg)

## Тестирование

### Auth Service (14 тестов)

![Тесты Auth Service](screenshots/10_tests_auth.jpg)

### Bot Service (13 тестов)

![Тесты Bot Service](screenshots/11_tests_bot.jpg)