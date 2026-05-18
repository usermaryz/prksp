#!/usr/bin/env bash
# Локальный запуск всех микросервисов WMS без Docker.
# Один раз: ./bootstrap_local.sh  (нужен Python 3.11 или 3.12; на 3.14 старые pydantic не ставятся)

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

VENV_BIN="${ROOT}/venv/bin"
if [[ ! -x "${VENV_BIN}/uvicorn" ]]; then
  echo "Нет venv или uvicorn. Создайте окружение и установите зависимости (см. комментарий в начале скрипта)."
  exit 1
fi

export PATH="${VENV_BIN}:$PATH"

cleanup() {
  echo ""
  echo "Останавливаю процессы..."
  for pid in $(jobs -p 2>/dev/null); do kill "$pid" 2>/dev/null || true; done
}
trap cleanup EXIT INT TERM

start_one() {
  local name=$1
  local port=$2
  local dir=$3
  echo "Starting $name on :$port ..."
  (cd "${ROOT}/${dir}" && exec uvicorn app.main:app --host 0.0.0.0 --port "$port")
}

start_one "Auth Service" 8001 "auth-service" &
sleep 0.5
start_one "Product Service" 8002 "product-service" &
sleep 0.5
start_one "Order Service" 8003 "order-service" &
sleep 0.5
start_one "Inventory Service" 8004 "inventory-service" &
sleep 0.5
start_one "Picking Service" 8005 "picking-service" &
sleep 0.5
start_one "Logistics Service" 8006 "logistics-service" &
sleep 1
start_one "API Gateway" 8000 "api-gateway" &

echo ""
echo "Бэкенд запущен:"
echo "  API Gateway:   http://localhost:8000  (документация: /api/docs)"
echo "  Auth … Logistics, Inventory — порты 8001–8006"
echo ""
echo "Фронтенд (в другом терминале):"
echo "  cd ${ROOT}/../wms_site && npm start"
echo ""
echo "Ctrl+C — остановить все сервисы."

wait
