#!/usr/bin/env bash
# Создаёт venv на Python 3.11/3.12, ставит зависимости и генерирует .env.local с секретами.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

PY="${PYTHON:-}"
if [[ -z "$PY" ]]; then
  for cand in python3.12 python3.11 python3; do
    if command -v "$cand" &>/dev/null; then
      ver="$($cand -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
      major="${ver%%.*}"
      minor="${ver#*.}"
      if [[ "$major" -eq 3 ]] && [[ "$minor" -ge 11 ]] && [[ "$minor" -le 12 ]]; then
        PY="$cand"
        break
      fi
    fi
  done
fi
if [[ -z "$PY" ]]; then
  echo "Нужен Python 3.11 или 3.12 (установите через Homebrew: brew install python@3.12)."
  exit 1
fi

echo "Using: $($PY --version)"
$PY -m venv venv
# shellcheck disable=SC1091
source venv/bin/activate
pip install -U pip wheel
for s in auth-service product-service order-service picking-service logistics-service inventory-service api-gateway; do
  echo "=== pip install $s ==="
  pip install -r "$s/requirements.txt"
done

ENV_FILE="${ROOT}/.env.local"
if [[ ! -f "$ENV_FILE" ]]; then
  cat > "$ENV_FILE" <<EOF
# Локальные секреты (не коммитить). Сгенерировано bootstrap_local.sh
SECRET_KEY=$(openssl rand -hex 32)
INTERNAL_API_KEY=$(openssl rand -hex 32)
ENABLE_DEMO_SEED=true
REDIS_URL=redis://localhost:6379/0
EOF
  echo ""
  echo "Создан ${ENV_FILE} с SECRET_KEY, INTERNAL_API_KEY и REDIS_URL."
else
  echo ""
  echo "${ENV_FILE} уже существует — секреты не перезаписаны."
fi

echo ""
echo "Готово. Запуск: ./start_all.sh"
echo "Redis обязателен: brew install redis && brew services start redis"
