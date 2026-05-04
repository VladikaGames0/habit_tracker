# Habit Tracker

Трекер привычек на Django REST Framework с Celery, Redis, PostgreSQL, Telegram-ботом и Docker.

## Технологии

- **Django 5** + **Django REST Framework**
- **PostgreSQL** — база данных
- **Redis** — брокер для Celery
- **Celery** + **django-celery-beat** — периодические задачи
- **Telegram Bot** — напоминания пользователям
- **Nginx** — веб-сервер
- **Docker** + **Docker Compose** — контейнеризация
- **GitHub Actions** — CI/CD

---

## Запуск локально (Docker)

### 1. Клонируй репозиторий

```bash
git clone https://github.com/VladikaGames0/habit_tracker.git
cd habit_tracker
```

### 2. Создай `.env` файл

```bash
cp .env.template .env
```

Заполни `.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=habit_db
DB_USER=habit_user
DB_PASSWORD=your-password
DB_HOST=db
DB_PORT=5432

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

TELEGRAM_BOT_TOKEN=your-bot-token

CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### 3. Запусти все сервисы одной командой

```bash
docker-compose up -d --build
```

Приложение будет доступно по адресу: `http://localhost`

### 4. Создай суперпользователя (опционально)

```bash
docker-compose exec web python manage.py createsuperuser
```

---

## Запуск без Docker (локально)

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Celery worker:
```bash
celery -A config worker -l info --pool=solo
```

Celery beat:
```bash
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

## API документация

- Swagger: `http://localhost/swagger/`
- ReDoc: `http://localhost/redoc/`

## Эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| POST | /api/users/register/ | Регистрация |
| POST | /api/users/login/ | Получение JWT токена |
| POST | /api/users/token/refresh/ | Обновление токена |
| GET/PATCH | /api/users/profile/ | Профиль пользователя |
| GET/POST | /api/habits/ | Список/создание привычек |
| GET/PUT/PATCH/DELETE | /api/habits/{id}/ | Операции с привычкой |
| GET | /api/habits/public/ | Публичные привычки |

---

## CI/CD (GitHub Actions)

Pipeline запускается при каждом `push` и `pull_request` в ветки `main` и `develop`.

### Этапы:

1. **Lint** — проверка кода через `flake8`
2. **Test** — запуск тестов через `pytest` с PostgreSQL и Redis
3. **Build** — сборка Docker-образа
4. **Deploy** — автоматический деплой на сервер (только при push в `main`)

### Необходимые GitHub Secrets:

| Secret | Описание |
|--------|----------|
| `SECRET_KEY` | Django секретный ключ |
| `SERVER_HOST` | IP адрес сервера |
| `SERVER_USER` | Пользователь SSH |
| `SERVER_SSH_KEY` | Приватный SSH ключ |
| `SERVER_PORT` | SSH порт (обычно 22) |

---

## Настройка сервера

### Требования:
- Ubuntu 22.04+
- Docker
- Docker Compose

### Шаги:

```bash
# Установка Docker
sudo apt update
sudo apt install -y docker.io git
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Клонирование проекта
git clone https://github.com/VladikaGames0/habit_tracker.git
cd habit_tracker
cp .env.template .env
# Заполни .env реальными значениями

# Запуск
docker-compose up -d --build
```

---

## Тесты

```bash
# Локально
pytest

# С покрытием
coverage run -m pytest
coverage report
```

---

## Как привязать Telegram

1. Найди бота и напиши `/start`
2. Укажи `telegram_chat_id` в профиле через `PATCH /api/users/profile/`
3. Настрой периодическую задачу в Django Admin → Periodic Tasks
