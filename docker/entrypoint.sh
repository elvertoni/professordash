#!/bin/bash
set -e

echo "Aguardando PostgreSQL em $DB_HOST:5432..."
while ! nc -z "${DB_HOST:-db}" 5432; do
  sleep 0.5
done
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
