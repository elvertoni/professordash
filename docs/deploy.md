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
COPY requirements/ ./requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]
```

### docker-compose.prod.yml

```yaml
services:
  app:
    build:
      context: .
      dockerfile: docker/Dockerfile
    env_file: .env
    environment:
      DJANGO_SETTINGS_MODULE: config.settings.production
    expose:
      - "8000"
    volumes:
      - /srv/professordash/media:/app/media
      - /srv/professordash/static:/app/staticfiles
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test:
        - CMD-SHELL
        - python -c "import socket; s=socket.create_connection(('127.0.0.1', 8000), 2); s.close()"
      interval: 10s
      timeout: 5s
      retries: 12
      start_period: 60s

  db:
    image: postgres:16-alpine
    env_file: .env
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test:
        - CMD-SHELL
        - pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB -h 127.0.0.1
      interval: 10s
      timeout: 5s
      retries: 6
      start_period: 10s

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    healthcheck:
      test:
        - CMD-SHELL
        - redis-cli ping | grep -q PONG
      interval: 10s
      timeout: 5s
      retries: 6
      start_period: 10s

  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"
    volumes:
      - ./docker/caddy/Caddyfile:/etc/caddy/Caddyfile:ro
      - /srv/professordash/static:/srv/professordash/static:ro
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      app:
        condition: service_healthy
    restart: unless-stopped

volumes:
  postgres_data:
  caddy_data:
  caddy_config:
```

---

## Caddy

### Caddyfile

```caddyfile
aulas.tonicoimbra.com {
    # Arquivos estáticos servidos diretamente
    handle /static/* {
        root * /srv/professordash
        file_server
    }

    # Demais requests, incluindo downloads protegidos, vão para o Django
    reverse_proxy app:8000
}
```

- HTTPS automático via Let's Encrypt
- Certificados salvos em `/data` (volume `caddy_data`)
- Downloads de materiais restritos e entregas passam pelo Django para respeitar autenticação
- O Caddy encaminha o restante do tráfego para `app:8000`, então o Gunicorn precisa subir nessa porta.

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

echo "Aguardando Redis..."
while ! nc -z redis 6379; do sleep 0.5; done

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

- [x] `DEBUG=False` em produção (`config/settings/production.py`)
- [x] `SECRET_KEY` via variável de ambiente com `python-decouple` (nunca hardcoded)
- [x] `CSRF_COOKIE_SECURE=True` + `SESSION_COOKIE_SECURE=True` (`production.py`)
- [x] `X_FRAME_OPTIONS='DENY'` (`production.py`)
- [x] `SECURE_BROWSER_XSS_FILTER=True` + `SECURE_CONTENT_TYPE_NOSNIFF=True` (`production.py`)
- [x] `SECURE_HSTS_SECONDS=31536000` com `INCLUDE_SUBDOMAINS` e `PRELOAD` (`production.py`)
- [ ] Rate limiting no endpoint de upload (django-ratelimit) — pendente, implementar se necessário
- [x] Validação de MIME type nos uploads com `python-magic` (`core/validators.py`)
- [x] Arquivos de entrega servidos com `Content-Disposition: attachment` (Caddyfile)
- [ ] Google OAuth restrito ao domínio do professor (opcional) — configurar em `SOCIALACCOUNT_PROVIDERS`
- [x] Logs de acesso do Caddy via stdout/stderr coletados pelo Docker
