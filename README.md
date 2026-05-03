![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![Tests](https://img.shields.io/badge/tests-19%20passed-brightgreen)
![Demo](https://raw.githubusercontent.com/stegruslan/master_app/master/screenshots/demo.gif)
# Seansa — онлайн-запись для специалистов

SaaS-сервис, позволяющий специалистам принимать записи от клиентов через персональную публичную страницу. Мастер настраивает услуги и расписание — клиент записывается без регистрации.

**Продакшен:** [seansa.ru](https://seansa.ru)

---

## Стек

| Слой | Технологии |
|------|-----------|
| Backend | Python 3.12, FastAPI |
| База данных | PostgreSQL, SQLAlchemy (async), Alembic |
| Авторизация | JWT (access 30 мин + refresh 30 дней), bcrypt |
| Уведомления | Telegram Bot, Email (SMTP) |
| Фронтенд | Vanilla JS, 3 HTML страницы |
| Инфраструктура | Docker, Docker Compose, Nginx, VPS (Ubuntu) |
| CI/CD | GitHub Actions |
| Тесты | pytest, pytest-asyncio, httpx |

---

## Структура проекта

| Папка | Назначение |
|-------|-----------|
| `api/` | Роуты: auth, master, services, schedule, bookings, public |
| `core/` | Config, database, dependencies, security, logging |
| `models/` | Master, Service, Booking, WorkSchedule, Subscription |
| `schemas/` | Pydantic схемы |
| `migrations/` | Alembic миграции |
| `tests/` | 19 тестов: auth, bookings, slots |
| `frontend/` | master.html, book.html, cancel.html |
| `admin/` | SQLAdmin — просмотр и редактирование таблиц |
| `nginx/` | nginx.conf |

---

## Что реализовано

- **Авторизация** — регистрация и логин по телефону, JWT access + refresh токены
- **Кабинет мастера** — управление профилем, услугами, расписанием, записями
- **Генерация слотов** — свободное время рассчитывается на основе расписания и существующих записей
- **Публичная страница** — клиент выбирает услугу → дату → время → оставляет контакты
- **Отмена записи** — клиент получает уникальный токен и может отменить самостоятельно
- **Уведомления** — Telegram-бот и email (SMTP) при создании и отмене записи
- **Админка** — SQLAdmin с авторизацией на `/admin`
- **Тесты** — 19 тестов, покрыты авторизация, CRUD услуг и записей, генерация слотов
- **Деплой** — Docker Compose + Nginx + SSL (Let's Encrypt) + CI/CD через GitHub Actions

---

## API

### Авторизация

| Метод | Роут | Описание |
|-------|------|----------|
| POST | `/auth/register` | Регистрация мастера |
| POST | `/auth/login` | Логин, получение токенов |
| POST | `/auth/refresh` | Обновление access токена |

### Кабинет мастера (JWT required)

| Метод | Роут | Описание |
|-------|------|----------|
| GET/PUT | `/master/me` | Профиль |
| GET/POST | `/services/` | Список / создать услугу |
| PUT/DELETE | `/services/{id}` | Обновить / удалить услугу |
| GET/PUT | `/schedule/{weekday}` | Расписание |
| GET | `/bookings/` | Список записей |
| PATCH | `/bookings/{id}/status` | Изменить статус |

### Публичные роуты (для клиентов)

| Метод | Роут | Описание |
|-------|------|----------|
| GET | `/book/{slug}` | Информация о мастере |
| GET | `/book/{slug}/services` | Услуги |
| GET | `/book/{slug}/slots` | Свободные слоты |
| POST | `/book/{slug}` | Создать запись |
| GET | `/cancel/{token}` | Отменить запись |

Документация: `/docs` (Swagger) · `/redoc`

---

## Запуск локально

```bash
git clone https://github.com/stegruslan/seansa.git
cd seansa

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env  # заполнить переменные

alembic upgrade head
uvicorn main:app --reload
```

Сервер: `http://localhost:8000`

### Переменные окружения

```env
DB_DIALECT=postgresql+asyncpg
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=seansa

SECRET_KEY=       # openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

ADMIN_PASSWORD=
ADMIN_SECRET_KEY= # openssl rand -hex 32
```

---

## Тесты

```bash
pip install pytest pytest-asyncio httpx aiosqlite
pytest tests/ -v
```

Используют SQLite in-memory — реальная БД не затрагивается.

---

## Планы

- Timezone для каждого мастера (сейчас UTC)
- Тарификация и план Pro
- SMS-верификация при отмене записи
