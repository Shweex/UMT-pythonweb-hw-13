# UMT-pythonweb-hw-13

Фінальне домашнє завдання до теми 13: Contacts REST API з документацією Sphinx, тестами, Redis-кешем, скиданням пароля та ролями користувачів.

## Можливості

- Реєстрація, логін, підтвердження email
- CRUD контактів, пошук, найближчі дні народження
- Кешування поточного користувача в Redis під час авторизації
- Скидання пароля через email
- Ролі `user` та `admin` (лише admin може змінювати аватар)
- Docker Compose: PostgreSQL + Redis + FastAPI

## Запуск

1. Скопіюйте `.env.example` у `.env` і заповніть значення.
2. Запустіть сервіси:

```bash
docker compose up --build
```

API буде доступне на `http://localhost:8000`.

## Тести

```bash
pip install -r requirements.txt
pytest --cov=app --cov-report=term-missing
```

## Документація Sphinx

```bash
cd docs
sphinx-build -b html . _build/html
```

## Основні ендпоінти

| Метод | Шлях | Опис |
|-------|------|------|
| POST | `/api/auth/register` | Реєстрація |
| POST | `/api/auth/login` | Логін (кешує користувача в Redis) |
| POST | `/api/auth/forgot-password` | Запит на скидання пароля |
| POST | `/api/auth/reset-password/{token}` | Підтвердження нового пароля |
| GET | `/api/users/me` | Профіль поточного користувача |
| PATCH | `/api/users/me/avatar` | Зміна аватара (тільки admin) |
| CRUD | `/api/contacts` | Управління контактами |

## Структура тестів

- `tests/unit/` — модульні тести репозиторіїв і сервісів
- `tests/integration/` — інтеграційні тести маршрутів API
