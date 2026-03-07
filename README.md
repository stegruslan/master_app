# Seansa — платформа онлайн-записи для специалистов.

Онлайн-сервис для записи клиентов к специалистам из различных сфер услуг.
Пользователь, предоставляющий услуги, регистрируется в системе, настраивает список услуг и рабочее расписание. После этого система генерирует публичную страницу специалиста, через которую клиенты могут записаться на свободное время без необходимости регистрации.

---

## Стек

- **Backend:** FastAPI + SQLAlchemy (async) + Alembic
- **База данных:** PostgreSQL
- **Авторизация:** JWT (access + refresh токены)
- **Админка:** SQLAdmin
- **Фронтенд:** Vanilla JS (3 HTML страницы)
- **Тесты:** pytest + pytest-asyncio + httpx

---

## Структура проекта

```
.
├── admin/
│   ├── setup.py          # Настройка SQLAdmin
│   └── views.py          # Представления таблиц в админке
├── api/
│   ├── auth.py           # Регистрация, логин, refresh токена
│   ├── bookings.py       # CRUD записей мастера
│   ├── master.py         # Профиль мастера
│   ├── public.py         # Публичные роуты для клиентов
│   ├── schedule.py       # Расписание мастера
│   └── services.py       # CRUD услуг
├── core/
│   ├── config.py         # Настройки через pydantic-settings
│   ├── database.py       # Подключение к БД, движок, сессии
│   ├── dependencies.py   # get_current_master
│   ├── logging.py        # Логирование
│   └── security.py       # Хэширование паролей, JWT
├── frontend/
│   ├── master.html       # Кабинет мастера
│   ├── book.html         # Страница записи клиента
│   └── cancel.html       # Отмена записи
├── migrations/           # Alembic миграции
├── models/
│   ├── booking.py        # Запись клиента
│   ├── schedule.py       # Расписание мастера
│   ├── service.py        # Услуга
│   ├── subscription.py   # Подписка мастера
│   └── user.py           # Мастер
├── schemas/              # Pydantic схемы
├── tests/
│   ├── conftest.py       # Фикстуры и тестовая БД
│   ├── test_auth.py      # Тесты авторизации
│   ├── test_bookings.py  # Тесты записей и услуг
│   └── test_slots.py     # Тесты генерации слотов
├── utils/
│   └── validators.py
├── main.py               # Точка входа FastAPI
└── .env                  # Переменные окружения
```

---

## Модели БД

### Master (мастер)
| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Первичный ключ |
| phone | String | Телефон (уникальный) |
| password_hash | String | Хэш пароля |
| name | String | Имя |
| email | String | Email (опционально) |
| slug | String | Уникальный идентификатор для публичной ссылки |
| is_active | Boolean | Активен ли аккаунт |

### Service (услуга)
| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Первичный ключ |
| master_id | Integer | FK → masters |
| name | String | Название услуги |
| duration | Integer | Длительность в минутах |
| price | Integer | Цена в рублях |
| is_active | Boolean | Активна ли услуга |

### Booking (запись)
| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Первичный ключ |
| master_id | Integer | FK → masters |
| service_id | Integer | FK → services |
| client_name | String | Имя клиента |
| client_phone | String | Телефон клиента |
| client_email | String | Email клиента (опционально) |
| datetime_start | DateTime | Начало записи (UTC) |
| datetime_end | DateTime | Конец записи (UTC) |
| status | String | pending / confirmed / cancelled |
| cancel_token | String | Токен для отмены записи клиентом |

### WorkSchedule (расписание)
| Поле | Тип | Описание |
|------|-----|----------|
| master_id | Integer | FK → masters |
| weekday | Integer | День недели (0=Пн, 6=Вс) |
| start_time | Time | Начало рабочего дня |
| end_time | Time | Конец рабочего дня |
| is_working | Boolean | Рабочий день или выходной |

### Subscription (подписка)
| Поле | Тип | Описание |
|------|-----|----------|
| master_id | Integer | FK → masters |
| plan | String | free / pro |
| is_active | Boolean | Активна ли подписка |
| expires_at | DateTime | Дата окончания подписки |

---

## Переменные окружения

Создай файл `.env` в корне проекта:

```env
# База данных
DB_DIALECT=postgresql+asyncpg
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=seansa

# JWT
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# Админка
ADMIN_PASSWORD=your_admin_password
ADMIN_SECRET_KEY=your_admin_secret_key
```

Сгенерировать `SECRET_KEY` и `ADMIN_SECRET_KEY`:
```bash
openssl rand -hex 32
```

---

## Установка и запуск

```bash
# Клонировать репозиторий
git clone https://github.com/yourname/seansa.git
cd seansa

# Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл и заполнить переменные
cp .env.example .env

# Применить миграции
alembic upgrade head

# Запустить сервер
uvicorn main:app --reload
```

Сервер запустится на `http://localhost:8000`

---

## API роуты

### Авторизация
| Метод | Роут | Описание |
|-------|------|----------|
| POST | `/auth/register` | Регистрация мастера |
| POST | `/auth/login` | Логин, получение токенов |
| POST | `/auth/refresh` | Обновление access токена |

### Кабинет мастера (требует авторизации)
| Метод | Роут | Описание |
|-------|------|----------|
| GET | `/master/me` | Получить профиль |
| PUT | `/master/me` | Обновить профиль |
| GET | `/services/` | Список услуг |
| POST | `/services/` | Создать услугу |
| PUT | `/services/{id}` | Обновить услугу |
| DELETE | `/services/{id}` | Удалить услугу |
| GET | `/schedule/` | Получить расписание |
| PUT | `/schedule/{weekday}` | Обновить день расписания |
| GET | `/bookings/` | Список записей |
| PATCH | `/bookings/{id}/status` | Изменить статус записи |

### Публичные роуты (для клиентов)
| Метод | Роут | Описание |
|-------|------|----------|
| GET | `/book/{slug}` | Информация о мастере |
| GET | `/book/{slug}/services` | Услуги мастера |
| GET | `/book/{slug}/slots` | Свободные слоты |
| POST | `/book/{slug}` | Создать запись |
| GET | `/cancel/{token}` | Отменить запись по токену |

### Документация
```
http://localhost:8000/docs      # Swagger UI
http://localhost:8000/redoc     # ReDoc
```

---

## Админка

Доступна по адресу `http://localhost:8000/admin`

Логин: `admin`  
Пароль: значение `ADMIN_PASSWORD` из `.env`

Позволяет просматривать и редактировать все таблицы: мастера, записи, услуги, расписание.

---

## Тесты

```bash
# Установить зависимости для тестов
pip install pytest pytest-asyncio httpx aiosqlite

# Запустить все тесты
pytest tests/ -v

# Запустить конкретный файл
pytest tests/test_auth.py -v
```

Тесты используют SQLite в памяти — реальная база данных не затрагивается.

---

## Фронтенд

Три статических HTML страницы в папке `frontend/`:

- **`master.html`** — кабинет мастера: записи, услуги, расписание
- **`book.html`** — страница записи клиента (4 шага: услуга → дата → время → данные)
- **`cancel.html`** — отмена записи по токену

Ссылка для записи клиента:
```
http://localhost:5500/frontend/book.html?master={slug}
```

---

## Миграции

```bash
# Создать новую миграцию
alembic revision --autogenerate -m "описание изменений"

# Применить миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1
```