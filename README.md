# PRKSP — мини-WMS (микросервисы)

Учебный fullstack: React (MVVM) + **6 микросервисов** + **API Gateway** + PostgreSQL (отдельная БД на сервис).

## Архитектура

```
Браузер → wms_site (nginx) → api-gateway :8000
                                ├── auth-service :8001      → auth_db
                                ├── product-service :8002   → product_db
                                ├── order-service :8003     → order_db
                                ├── inventory-service :8004 → inventory_db
                                ├── picking-service :8005   → picking_db
                                └── logistics-service :8006 → logistics_db
```

Контракты API: `wms_api/api-contracts.yaml`.  
Старый монолит FastAPI: `legacy/backend_fastapi/` (не используется в Docker).

## Быстрый старт (Docker)

Из корня репозитория:

```bash
export SECRET_KEY="$(openssl rand -hex 32)"
export INTERNAL_API_KEY="$(openssl rand -hex 32)"
docker compose up --build
```

- **Интерфейс:** http://localhost:8080  
- **API Gateway:** http://localhost:8000  
- **Swagger:** http://localhost:8000/api/docs  

Демо-логины (при `ENABLE_DEMO_SEED=true`, по умолчанию): `admin` / `admin`, `manager` / `manager`, `picker` / `picker`.  
Отключить сид: `ENABLE_DEMO_SEED=false`. Redis используется для rate-limit (gateway), кэша и ревокации refresh-токенов.

Остановка: `docker compose down`. Данные PostgreSQL в именованных томах.

## Локальная разработка (без Docker)

1. Один раз — venv и секреты:

```bash
cd microservices
PYTHON=python3.12 ./bootstrap_local.sh   # создаёт venv и .env.local
brew install redis && brew services start redis   # обязательно для Redis
```

2. Бэкенд:

```bash
cd microservices
./start_all.sh
```

3. Фронт:

```bash
cd wms_site && npm install && npm start
```

Открыть http://localhost:3000 — webpack проксирует `/api` на gateway (:8000).

**Если что-то не работает:**
- `Redis недоступен` — `brew services start redis`
- Пустой склад / 401 — перелогиньтесь (`admin` / `admin`)
- Сброс локальных SQLite-БД: `cd microservices && ./reset_demo_dbs.sh && ./start_all.sh`

## Локальная разработка (фронт + Docker gateway)

1. Поднять бэкенд в Docker:

```bash
export SECRET_KEY="$(openssl rand -hex 32)"
export INTERNAL_API_KEY="$(openssl rand -hex 32)"
docker compose up --build
```

2. Фронт:

```bash
cd wms_site
npm install
npm start
```

Открыть http://localhost:3000 — webpack проксирует `/api` на gateway (:8000).

## Production-like (один порт 80)

```bash
export SECRET_KEY="$(openssl rand -hex 32)"
export INTERNAL_API_KEY="$(openssl rand -hex 32)"
docker compose -f docker-compose.prod.yml up -d --build
```

Открыть http://localhost/

## Структура репозитория

| Путь | Назначение |
|------|------------|
| `microservices/` | api-gateway, auth, product, order, inventory, picking, logistics |
| `wms_site/` | React + MobX (models / viewmodels / views) |
| `wms_api/` | OpenAPI-контракты |
| `docker-compose.yml` | полный стек для разработки |
| `tools/fuzz_api.py` | фаззинг gateway (`--base http://127.0.0.1:8000`) |

## Тесты

```bash
# E2E (нужны gateway :8000 и npm start :3000)
cd wms_site && npm run test:e2e

# Component (только Node)
cd wms_site && npm run test:component

# Фаззинг
python3 tools/fuzz_api.py --base http://127.0.0.1:8000 --rounds 60
```
