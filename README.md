# PRKSP

Учебный fullstack-проект «мини-WMS»: React (клиент) + FastAPI + SQLite. В репозитории есть Docker, тестовые данные при первом старте и черновики текстов под курсовую (в `docs/`). Сам отчёт по ГОСТ 7.32-2017 здесь не вкладывался — только исходники и вспомогательные материалы.

## Структура

| Папка | Назначение |
|--------|------------|
| `wms_site/` | Frontend, Webpack dev server |
| `backend_fastapi/` | REST API, модели SQLAlchemy, сиды |
| `docs/` | Предметная область, технологии, UML (Mermaid), облако, план презентации |
| `tools/fuzz_api.py` | Простой скрипт фаззинга API (ищет необработанные 5xx) |

## Демо-доступы (после сида БД)

Логин задаётся парой **логин / пароль**:

- `admin` / `admin`
- `manager` / `manager`
- `picker` / `picker`
- `driver` / `driver`

Роли отличаются по правам (например, сборщик не может самовольно перевести заказ в «отправлен» — сервер ответит `403`).

## Как запустить проект

Ниже 2 варианта: обычный локальный запуск и запуск через Docker.

## Вариант 1: локально (без Docker)

### Шаг 0. Перейти в проект

```bash
cd /Users/mary/Desktop/kursach_august/prksp
```

### Backend

```bash
cd backend_fastapi
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Переменные окружения (необязательно): `SECRET_KEY`, `DB_URL` (по умолчанию SQLite в `backend_fastapi/data/`).

Оставьте этот терминал открытым. Backend будет работать на `http://localhost:8000`. Быстрая проверка: `curl -s http://127.0.0.1:8000/health`.

### Frontend (во втором терминале)

```bash
cd /Users/mary/Desktop/kursach_august/prksp
cd wms_site
npm install
npm start
```

Адрес интерфейса: `http://localhost:3000`, API: `http://localhost:8000`.  
URL API на этапе сборки задаётся переменной **`REACT_APP_API_URL`** (см. `webpack.config.js`).

## Вариант 2: через Docker Compose

Из корня `prksp`:

```bash
docker compose up --build
```

- Frontend: `http://localhost:8080`
- API: `http://localhost:8000`  
При сборке веба можно переопределить `REACT_APP_API_URL`, если API доступен по другому адресу с точки зрения браузера.
- Проверка nginx: `curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/` (ожидается `200`).

Остановить контейнеры:

```bash
docker compose down
```

## Фаззинг-тестирование

Поднять backend, затем в другом терминале:

```bash
python3 tools/fuzz_api.py --base http://127.0.0.1:8000 --rounds 60
```

Скрипт гоняет случайные параметры и регистрации с «ломаными» ролями. Ожидаемые ответы — в основном `401/403/422`, но не `500`. Лог можно сохранить в файл и включить как иллюстрацию в записку. Перед прогоном убедитесь, что API уже поднят.

## Соответствие требованиям (что закрывает репозиторий)

1. Анализ предметной области — `docs/predmetnaya-oblast.md`.
2. Обоснование стека — `docs/tehnologii.md`.
3. Архитектура и UML-заготовки — `docs/uml.md` (+ экспорт в draw.io при необходимости).
4. Серверная логика и REST — код в `backend_fastapi/app/` (JWT, роли, бизнес-правила отправлений и сборки).
5. Логика уровня БД — модели и SQLite.
6. Клиентский слой — `wms_site/src/`.
7. Презентация — каркас слайдов `docs/prezentatsiya.md`.
8. Отчёт по ГОСТ — не входит в репозиторий (оформляется отдельно).

Дополнительно: Dockerfile’ы, `docker-compose.yml`, раздел про облако в `docs/cloud-deploy.md`.
