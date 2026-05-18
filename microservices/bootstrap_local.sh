#!/usr/bin/env bash
# Создаёт venv на Python 3.11/3.12 и ставит зависимости всех сервисов (без Docker).
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
echo ""
echo "Готово. Запуск: ./start_all.sh"
