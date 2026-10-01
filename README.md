Tennis Match Scoreboard

Веб-приложение для ведения счёта теннисного матча.
Проект реализован как учебное client-server приложение без использования полноценного web framework. 
Основная цель — практика построения многослойного веб-приложения, работы с HTTP/WSGI, SQLAlchemy, 
транзакциями и Docker deployment.

Возможности

создание нового теннисного матча;
подсчёт очков, games и sets;
поддержка deuce, advantage и tie-break;
определение победителя матча;
просмотр завершённых матчей;
фильтрация матчей по имени игрока;
пагинация;
валидация имён игроков;
сохранение данных в MySQL;
unit tests.

Технологии

Python 3.13
Werkzeug — HTTP/WSGI
Jinja2 — HTML templates
SQLAlchemy 2.0 — ORM и работа с БД
PyMySQL — MySQL driver
MySQL 8.4 — database
Waitress — production WSGI server
unittest — testing
Docker / Docker Compose — deployment
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

application/        Application Services и DTO
controllers/        HTTP Controllers
models/             Domain Models
services/           Domain Services
repositories/       Persistence layer
orm_models/         SQLAlchemy Models
mappers/            Mapping между слоями
unit_of_work/       Transaction management
validators/         Input validation
presentation/       Template rendering
wsgi_application/   WSGI и static files
templates/          HTML templates
static/             CSS, JavaScript и images

Запуск

Для запуска приложения используется Docker Compose. Docker Compose поднимает два контейнера:
приложение Tennis Match Scoreboard;
MySQL 8.4.

Требования
Docker
Docker Compose
Локальный запуск
Клонировать репозиторий и перейти в каталог проекта:
git clone https://github.com/Vadim-Neshitoi/Tennis-Match-Scoreboard
cd Tennis-Match-Scoreboard

Запустить приложение:
docker compose up -d --build
Проверить состояние контейнеров:
docker compose ps
После запуска приложение доступно по адресу:
http://localhost:8080

Остановить приложение:
docker compose down
Запуск на удалённом сервере
Подключиться к серверу по SSH и перейти в каталог проекта:
git clone https://github.com/Vadim-Neshitoi/Tennis-Match-Scoreboard
cd Tennis-Match-Scoreboard

Запустить приложение в фоновом режиме:
docker compose up -d --build
Проверить состояние контейнеров:
docker compose ps
После запуска приложение доступно по адресу:
http://<server-ip>:8080
Контейнеры продолжают работать после завершения SSH-сессии.
Обновление приложения на сервере
После публикации изменений в GitHub подключиться к серверу по SSH и перейти в каталог проекта:
cd Tennis-Match-Scoreboard
Получить последние изменения:
git pull
Пересобрать и перезапустить приложение:
docker compose up -d --build
Проверить состояние контейнеров:
docker compose ps

Тесты

Тесты проекта написаны с использованием стандартного модуля Python unittest.
Для запуска всех тестов:

python -m unittest discover

HTTP Endpoints

GET  /
GET  /new-match
POST /new-match
GET  /match-score?uuid=<uuid>
POST /match-score?uuid=<uuid>
GET  /matches?page=<page>&filter_by_player_name=<name>