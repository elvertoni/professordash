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

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings=config.settings.production

echo "Executando migrations..."
python manage.py migrate --noinput --settings=config.settings.production

echo "Atualizando domínio do Site (django.contrib.sites)..."
python manage.py shell --settings=config.settings.production -c "
from django.contrib.sites.models import Site
Site.objects.update_or_create(id=1, defaults={'domain': 'aulas.tonicoimbra.com', 'name': 'ProfessorDash'})
print('Site atualizado: aulas.tonicoimbra.com')
"

echo "Criando superuser se não existir..."
python manage.py shell --settings=config.settings.production -c "
from django.contrib.auth import get_user_model
import os
User = get_user_model()
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
if email and password and not User.objects.filter(email=email).exists():
    username = email.split('@')[0] if email else 'admin'
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser {email} criado com username {username}.')
else:
    print('Superuser já existe ou variáveis não definidas.')
"

exec "$@"
