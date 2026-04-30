# Habit Tracker — инструкция по запуску

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Запуск (Windows)

Открой **4 отдельных окна PowerShell** в папке проекта.

### Окно 1 — Django сервер
```powershell
python manage.py migrate
python manage.py runserver
```

### Окно 2 — Celery worker
```powershell
celery -A config worker -l info --pool=solo
```

### Окно 3 — Celery beat (расписание)
```powershell
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Окно 4 — Telegram бот
```powershell
python telegram_bot/bot.py
```

## Настройка периодических задач

1. Зайди в http://localhost:8000/admin/
2. Создай суперпользователя: `python manage.py createsuperuser`
3. Перейди в **Periodic Tasks → Add**
4. Создай задачу:
   - Name: `Send habit reminders`
   - Task: `habits.tasks.check_and_send_reminders`
   - Crontab: `* * * * *` (каждую минуту)

## API документация

- Swagger: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

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

## Как привязать Telegram

1. Найди бота и напиши `/start`
2. Если твой Telegram username совпадает с username на сайте — привязка произойдёт автоматически
3. Иначе бот покажет твой Chat ID — укажи его через `PATCH /api/users/profile/`

## Тесты

```bash
# Запуск тестов
pytest

# С покрытием
coverage run -m pytest
coverage report
```
