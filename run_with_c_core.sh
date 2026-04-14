#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "[1/4] Building C core..."
make -C c_core

if [[ ! -f c_core/libscheduler_dsa.so ]]; then
  echo "ERROR: c_core/libscheduler_dsa.so was not built."
  exit 1
fi

echo "[2/4] Running C core unit tests..."
make -C c_core test

echo "[3/4] Applying Django migrations..."
python manage.py migrate --noinput

echo "[4/4] Starting Django with C core enabled on http://127.0.0.1:8000"
echo "Tip: use CTRL+C to stop."
python manage.py runserver 127.0.0.1:8000
