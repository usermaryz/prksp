# Архитектура и UML (как оформить графику)

Ниже — заготовки под диаграммы. В отчёт обычно вставляют экспорт из PlantUML, draw.io или StarUML. Для быстрого превью можно открыть Mermaid в VS Code / на GitHub.

## 1. Компоненты (client–server)

```mermaid
flowchart LR
  subgraph client [Клиент]
    UI[React SPA]
  end
  subgraph server [Сервер]
    API[FastAPI REST]
    AUTH[JWT / роли]
    LOG[Бизнес-правила]
  end
  subgraph data [Данные]
    DB[(SQLite)]
  end
  UI -->|HTTPS JSON| API
  API --> AUTH
  API --> LOG
  LOG --> DB
```

## 2. Последовательность: логин

```mermaid
sequenceDiagram
  participant B as Браузер
  participant A as FastAPI /auth/login
  participant D as SQLite
  B->>A: POST логин/пароль (form)
  A->>D: найти пользователя
  D-->>A: hash + роль
  A-->>B: access_token + profile
```

## 3. Последовательность: операция с проверкой роли

```mermaid
sequenceDiagram
  participant B as Браузер
  participant A as FastAPI + Depends
  participant D as SQLite
  B->>A: PATCH /orders/{id}/status + Bearer
  A->>A: проверить JWT + роль
  alt роль не подходит
    A-->>B: 403
  else ок
    A->>D: обновить заказ
    D-->>A: ok
    A-->>B: 200 JSON
  end
```

## 4. Деплой (Docker)

```mermaid
flowchart TB
  U[Пользователь] --> N[Nginx :80 статика]
  U -->|/api| P[FastAPI :8000]
  P --> V[(volume data/prksp.db)]
```
