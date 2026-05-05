# WMS Backend Server

Сервер для тестирования API системы управления складом (WMS).

## Установка

1. Перейдите в директорию сервера:
```bash
cd server
```

2. Установите зависимости:
```bash
npm install
```

## Запуск

Для запуска в режиме разработки (с автоматической перезагрузкой):
```bash
npm run dev
```

Для запуска в production режиме:
```bash
npm start
```

Сервер будет доступен по адресу: http://localhost:3001

## API Endpoints

### Продукты

- `GET /api/placement/products` - получить список всех продуктов
- `GET /api/placement/products/search?q=query` - поиск продуктов
- `PATCH /api/placement/products/:id` - обновить местоположение продукта

### Зоны размещения

- `GET /api/placement/zones` - получить список всех зон размещения
- `GET /api/placement/zones/search?q=query` - поиск зон размещения

## Примеры запросов

### Обновление местоположения продукта
```bash
curl -X PATCH http://localhost:3001/api/placement/products/1 \
  -H "Content-Type: application/json" \
  -d '{"location": "A-12-3"}'
```

### Поиск продуктов
```bash
curl "http://localhost:3001/api/placement/products/search?q=наушники"
```

### Поиск зон
```bash
curl "http://localhost:3001/api/placement/zones/search?q=зона"
``` 