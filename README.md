# PRKSP — мини-WMS для курсовой

Учебный fullstack: веб-интерфейс (React) + REST API (FastAPI) + SQLite. После первого запуска в базе появляются демо-пользователи, товары и заказы — можно сразу кликать по интерфейсу, не заполняя всё вручную.






---

## Что внутри репозитория

| Папка / файл | Зачем |
|--------------|--------|
| `backend_fastapi/` | API, модели, JWT, сиды |
| `wms_site/` | фронт (Webpack + Cypress) |
| `docker-compose.yml` | локальный запуск в двух контейнерах |
| `docker-compose.prod.yml` | один хост: веб на :80, API за nginx по `/api` |
| `render.yaml` | blueprint для деплоя на Render |
| `tools/fuzz_api.py` | проверка API на «падения» (ответы 5xx) |
| `docs/` | материалы к курсовой, в т.ч. `cloud-deploy.md` |

---

## Что поставить на машину

- **Python 3.11+** — backend и фаззинг  
- **Node.js 18+** и **npm** — фронт и Cypress  
- **Docker** (по желанию) — если не хотите возиться с venv локально  

---

## Быстрый старт (локально, два терминала)

Удобнее всего для разработки и для **всех тестов**, кроме component Cypress.

**Терминал 1 — API**

```bash
cd backend_fastapi
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Проверка: `curl http://127.0.0.1:8000/health` → `{"status":"ok"}`.

**Терминал 2 — интерфейс**

```bash
cd wms_site
npm install
npm start
```

Открыть **http://localhost:3000**. Войти, например: **admin** / **admin**.

Другие роли после сида: `manager` / `manager`, `picker` / `picker`, `driver` / `driver`. У ролей разные права — часть кнопок на API ответит `403`, это нормально.

---

## Запуск через Docker

Из **корня** репозитория (где лежит `docker-compose.yml`):

```bash
docker compose up --build
```

- интерфейс: **http://localhost:8080**  
- API: **http://localhost:8000**  

Остановить: `docker compose down`. Данные SQLite в Docker хранятся в томе `prksp-db` и не пропадают после `down`, пока том явно не удалить.

**На VPS / для «продакшн-подобного» варианта** (один порт 80, API проксируется nginx):

```bash
export SECRET_KEY="$(openssl rand -hex 32)"
docker compose -f docker-compose.prod.yml up -d --build
```

Подробнее про облако (Render, переменные) — **`docs/cloud-deploy.md`**.

---

## Тестирование

Логика такая: сначала поднимаете то, что нужно конкретному виду теста, потом одна команда из `wms_site` или из корня.

### Сводка

| Что проверяем | Команда | Что должно быть запущено |
|---------------|---------|---------------------------|
| UI в браузере (E2E) | `npm run test:e2e` | API на :8000 **и** фронт на :3000 |
| Кнопки, поля, таблица (component) | `npm run test:component` | только Node (Cypress сам поднимет webpack) |
| Устойчивость API (фаззинг) | `python3 tools/fuzz_api.py …` | только API на :8000 |

Интерактивный режим Cypress (удобно при отладке): `npm run test:e2e:open` и `npm run test:component:open`.

---

### Cypress: end-to-end

Проверяются сценарии «как пользователь»: вход, список заказов, фильтры, модалка создания заказа. Спеки в `wms_site/cypress/e2e/` (`auth.cy.ts`, `orders.cy.ts`).

**Порядок действий**

1. В первом терминале — API (см. выше).  
2. Во втором — `cd wms_site && npm start` (порт **3000**).  
3. В третьем:

```bash
cd wms_site
npm run test:e2e
```

Ожидаемый результат в конце: `All specs passed` (6 тестов в двух файлах).

---

### Cypress: component-тесты

Изолированно монтируются общие компоненты (`Button`, `Input`, `Table`) — файлы `*.cy.tsx` рядом с компонентами в `wms_site/src/components/common/`.

API и `npm start` **не нужны**:

```bash
cd wms_site
npm install   # если ещё не ставили зависимости
npm run test:component
```

Ожидаемо: **20** проходящих тестов в трёх спеках.

---

### Фаззинг API

Скрипт шлёт на API случайные и заведомо кривые запросы (параметры, JSON, токены). Успех прогона — **ни одного ответа 5xx**; `401`, `422` и т.п. допустимы.

Из **корня** репозитория, пока API слушает :8000:

```bash
python3 tools/fuzz_api.py --base http://127.0.0.1:8000 --rounds 60
```

Сохранить отчёт для записки:

```bash
python3 tools/fuzz_api.py --base http://127.0.0.1:8000 --rounds 100 --json-log fuzz_report.json
```

Повторяемость: флаг `--seed 42`.

---

### Если что-то упало

| Ситуация | Что проверить |
|----------|----------------|
| E2E не находит поля на `/login` | фронт на :3000, API на :8000; не закрыли терминалы |
| E2E таймаут на логине | API не поднят или неверный `REACT_APP_API_URL` |
| `Address already in use` :8000 | остановить старый `uvicorn` или сменить порт |
| Docker: `web` падает с nginx upstream | в `wms_site/nginx.conf` хост прокси — **`api`**, как в `docker-compose.yml` |
| Фаззинг сразу «сервер недоступен» | сначала `curl …/health` |
| Component-тесты | достаточно `npm install` в `wms_site` |

Скриншоты упавших E2E Cypress кладёт в `wms_site/cypress/screenshots/` — в git они не нужны (см. `wms_site/.gitignore`).
