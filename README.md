Tennis Match Scoreboard
Веб-приложение для ведения счёта теннисного матча.
Проект реализован как учебное client-server приложение без использования полноценного web framework.
Основная цель — практика построения многослойного веб-приложения, работы с HTTP/WSGI, SQLAlchemy и транзакциями.

Возможности
- создание нового теннисного матча;
- подсчёт очков, games, sets, deuce, advantage и tie-break;
- определение победителя матча;
- просмотр завершённых матчей;
- фильтрация матчей по имени игрока;
- пагинация;
- валидация имён игроков;
- сохранение данных в MySQL;
- database migrations через Alembic;
- unit tests.

Технологии
- Python 3.13
- Werkzeug — HTTP/WSGI
- Jinja2 — HTML templates
- SQLAlchemy 2.0 — ORM и работа с БД
- PyMySQL — MySQL driver
- Alembic — database migrations
- MySQL 8 — database
- Waitress — production WSGI server
- pytest — testing
- Poetry — dependency management
  Frontend реализован на чистом HTML/CSS/JavaScript, без Bootstrap и других UI-фреймворков.

Архитектура
Проект использует многослойную архитектуру с разделением ответственности:
HTTP
  ↓
WSGIApplication
  ↓
Controllers
  ↓
Application Services
  ↓
Domain
  ↓
Repositories
  ↓
UnitOfWork
  ↓
SQLAlchemy / MySQL

Основные директории:
application/       Application Services и DTO
controllers/       HTTP Controllers
models/            Domain Models
services/          Domain Services
repositories/      Persistence layer
orm_models/        SQLAlchemy Models
mappers/           Mapping между слоями
unit_of_work/      Transaction management
validators/        Input validation
presentation/      Template rendering
wsgi_application/  WSGI и static files
templates/         HTML templates
static/            CSS, JavaScript и images

Запуск
Требования
- Python 3.13
- MySQL 8
- Poetry
Установка
Клонировать репозиторий и установить зависимости:
poetry install

Создать MySQL database и настроить переменную окружения:
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/tennis_match_scoreboard

Применить migrations:
poetry run alembic upgrade head

Запустить приложение:
poetry run python main.py

По умолчанию приложение доступно по адресу:
http://localhost:8080

Тесты
poetry run pytest

HTTP Endpoints
GET  /
GET  /new-match
POST /new-match
GET  /match-score?uuid=<uuid>
POST /match-score?uuid=<uuid>
GET  /matches?page=<page>&filter_by_player_name=<name>