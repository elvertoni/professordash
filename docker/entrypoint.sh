#!/bin/bash
set -e

echo "Aguardando PostgreSQL verificar conexao via DATABASE_URL..."
python -c "
import os, sys, time, psycopg2
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print('DATABASE_URL nao configurada, ignorando wait.')
    sys.exit(0)
while True:
    try:
        conn = psycopg2.connect(db_url)
        conn.close()
        break
    except psycopg2.OperationalError:
        print('Aguardando banco...')
        time.sleep(1)
"
echo "PostgreSQL disponível."

echo "Executando migrations..."
python manage.py migrate --noinput --settings=config.settings.production

echo "Criando superuser se não existir..."
python manage.py shell --settings=config.settings.production -c "
from django.contrib.auth import get_user_model
import os
User = get_user_model()
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
if email and password and not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=password)
    print(f'Superuser {email} criado.')
else:
    print('Superuser já existe ou variáveis não definidas.')
"

exec "$@"
