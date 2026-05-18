#!/usr/bin/env bash
# Удаляет локальные SQLite БД — при следующем запуске start_all.sh данные создадутся заново.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

dbs=(
  "$ROOT/auth-service/auth.db"
  "$ROOT/product-service/products.db"
  "$ROOT/order-service/orders.db"
  "$ROOT/inventory-service/inventory.db"
  "$ROOT/picking-service/picking.db"
  "$ROOT/logistics-service/logistics.db"
)

for f in "${dbs[@]}"; do
  if [[ -f "$f" ]]; then
    rm -f "$f"
    echo "Удалено: $f"
  fi
done

echo ""
echo "Готово. Перезапустите бэкенд: ./start_all.sh"
