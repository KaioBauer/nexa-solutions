#!/bin/sh
set -e

POSTGRES_HOST="${POSTGRES_HOST:-db}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

echo "Aguardando banco de dados em ${POSTGRES_HOST}:${POSTGRES_PORT}..."

until python - <<PYEOF
import socket
import sys

try:
    with socket.create_connection(("${POSTGRES_HOST}", ${POSTGRES_PORT}), timeout=1):
        sys.exit(0)
except OSError:
    sys.exit(1)
PYEOF
do
  sleep 1
done

echo "Banco de dados disponível. Aplicando migrations..."
python manage.py migrate --noinput

exec "$@"
