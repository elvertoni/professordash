#!/bin/bash
set -e

echo "Aguardando PostgreSQL e Redis ficarem prontos..."
python - <<'PY'
import os
import time

import psycopg2
import redis


def wait_for_postgres():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL nao configurada, ignorando wait do PostgreSQL.")
        return

    while True:
        try:
            conn = psycopg2.connect(db_url)
            conn.close()
            print("PostgreSQL disponivel.")
            return
        except psycopg2.OperationalError:
            print("Aguardando PostgreSQL...")
            time.sleep(1)


def wait_for_redis():
    redis_url = os.environ.get("REDIS_URL")
    if not redis_url:
        print("REDIS_URL nao configurada, ignorando wait do Redis.")
        return

    client = redis.Redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2)
    while True:
        try:
            client.ping()
            print("Redis disponivel.")
            return
        except redis.exceptions.RedisError:
            print("Aguardando Redis...")
            time.sleep(1)


wait_for_postgres()
wait_for_redis()
PY

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings=config.settings.production

echo "Executando migrations..."
python manage.py migrate --noinput --settings=config.settings.production

echo "Sincronizando domínio do Site e Google OAuth..."
python manage.py sync_auth_setup --settings=config.settings.production

echo "Configurando superuser..."
python manage.py shell --settings=config.settings.production -c "
from django.contrib.auth import get_user_model
import os
User = get_user_model()
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '').strip()
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '').strip()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', '').strip()

try:
    if not email or not password:
        print('DJANGO_SUPERUSER_EMAIL/DJANGO_SUPERUSER_PASSWORD ausentes. Superuser não será alterado.')
    else:
        username = username or email.split('@', 1)[0]
        user = User.objects.filter(email=email).first()
        if user:
            print(f'Superuser {email} já existe. Mantendo credenciais atuais.')
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f'Superuser {email} criado.')
except Exception as e:
    print(f'Erro ao configurar superuser: {e}')
"

exec "$@"
