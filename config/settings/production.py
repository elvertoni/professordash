import urllib.parse
from decouple import config

from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="aulas.tonicoimbra.com",
    cast=lambda v: [h.strip() for h in v.split(",")],
)

CSRF_TRUSTED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS
] + ["http://localhost:8000"]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# --- Banco de dados ---

db_url = config("DATABASE_URL", default="")
if db_url:
    parsed_db = urllib.parse.urlparse(db_url)
    db_options = {}
    db_query = urllib.parse.parse_qs(parsed_db.query)
    if "sslmode" in db_query:
        db_options["sslmode"] = db_query["sslmode"][-1]

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": urllib.parse.unquote(parsed_db.path.lstrip("/")),
            "USER": urllib.parse.unquote(parsed_db.username or ""),
            "PASSWORD": urllib.parse.unquote(parsed_db.password or ""),
            "HOST": parsed_db.hostname or "db",
            "PORT": parsed_db.port or 5432,
            **({"OPTIONS": db_options} if db_options else {}),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("POSTGRES_DB", default="professordash"),
            "USER": config("POSTGRES_USER", default="prof"),
            "PASSWORD": config("POSTGRES_PASSWORD", default=""),
            "HOST": config("DB_HOST", default="db"),
            "PORT": config("DB_PORT", default=5432, cast=int),
        }
    }

# --- Cache e sessões com Redis ---

REDIS_URL = config("REDIS_URL", default="redis://redis:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# --- Segurança ---

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# --- E-mail ---

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
