# Deploy — ProfessorDash

## Docker e Compose

### Dockerfile

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    libmagic1 libpango-1.0-0 libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements/production.txt .
RUN pip install --no-cache-dir -r production.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

### docker-compose.prod.yml

```yaml
version: "3.9"

services:
  app:
    build: .
    env_file: .env
    volumes:
      - /srv/professordash/media:/app/media
      - /srv/professordash/static:/app/staticfiles
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    env_file: .env
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/caddy/Caddyfile:/etc/caddy/Caddyfile
      - /srv/professordash/media:/srv/professordash/media:ro
      - /srv/professordash/static:/srv/professordash/static:ro
      - caddy_data:/data
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  caddy_data:
```

---

## Caddy

### Caddyfile

```caddyfile
aulas.tonicoimbra.com {
    # Arquivos de mídia servidos diretamente (sem passar pelo Django)
    handle /media/* {
        root * /srv/professordash
        file_server
        header Content-Disposition "attachment"
    }

    # Demais requests → Gunicorn
    reverse_proxy app:8000
}
```

- HTTPS automático via Let's Encrypt
- Certificados salvos em `/data` (volume `caddy_data`)
- Media servido diretamente com `Content-Disposition: attachment` para forçar download

---

## Variáveis de Ambiente (.env)

```env
# Django
SECRET_KEY=change-me-in-production
DEBUG=False
ALLOWED_HOSTS=aulas.tonicoimbra.com,localhost

# Superuser
DJANGO_SUPERUSER_EMAIL=toni@tonicoimbra.com
DJANGO_SUPERUSER_PASSWORD=senha-segura-aqui

# PostgreSQL
POSTGRES_DB=professordash
POSTGRES_USER=prof
POSTGRES_PASSWORD=senha-db-aqui
DATABASE_URL=postgresql://prof:senha-db-aqui@db:5432/professordash

# Redis
REDIS_URL=redis://redis:6379/0

# Google OAuth
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx

# Email (opcional — para notificações futuras)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

---

## entrypoint.sh

```bash
#!/bin/bash
set -e

echo "Aguardando PostgreSQL..."
while ! nc -z db 5432; do sleep 0.5; done

echo "Executando migrations..."
python manage.py migrate --noinput

echo "Criando superuser se não existir..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser criado.')
"

exec "$@"
```

---

## Backup

Cron job (`/etc/cron.d/professordash-backup`):

```bash
# Dump PostgreSQL diário às 2h
0 2 * * * root docker exec professordash-db-1 \
  pg_dump -U prof professordash | gzip \
  > /srv/backups/db_$(date +\%Y\%m\%d).sql.gz

# Backup de arquivos de media às 3h
0 3 * * * root tar -czf \
  /srv/backups/media_$(date +\%Y\%m\%d).tar.gz \
  /srv/professordash/media/

# Manter apenas últimos 30 dias
0 4 * * * root find /srv/backups/ -mtime +30 -delete
```

---

## Estrutura de Pastas na VPS

```
/srv/professordash/
├── media/              ← arquivos upados (bind mount)
├── static/             ← arquivos estáticos (collectstatic)
└── .env                ← variáveis de ambiente

/etc/cron.d/
└── professordash-backup    ← jobs de backup

/srv/backups/
├── db_20260315.sql.gz
├── media_20260315.tar.gz
└── ...
```

---

## Checklist de Segurança

- [ ] `DEBUG=False` em produção
- [ ] `SECRET_KEY` única e segura (32+ chars aleatórios)
- [ ] `CSRF_COOKIE_SECURE=True` + `SESSION_COOKIE_SECURE=True`
- [ ] `X_FRAME_OPTIONS='DENY'`
- [ ] `SECURE_BROWSER_XSS_FILTER=True`
- [ ] Rate limiting no endpoint de upload (django-ratelimit)
- [ ] Validação de MIME type nos uploads (python-magic)
- [ ] Arquivos de entrega servidos com `Content-Disposition: attachment`
- [ ] Google OAuth configurado apenas para domínio do professor (opcional)
- [ ] Logs de acesso ativados no Caddy
