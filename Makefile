# Makefile — ProfessorDash
# Comandos utilitários para desenvolvimento local.
# Compatível com SQLite (dev) e PostgreSQL (prod).

.PHONY: help reset seed setup migrate shell test clean

help: ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Banco de dados
# ---------------------------------------------------------------------------

DB_ENGINE := $(shell python -c "from django.conf import settings; \
	from django.db import connection; \
	print(connection.vendor)" 2>/dev/null || echo "sqlite")

reset: ## Remove e recria o banco de dados, aplica migrations
	@echo "=== Resetando banco de dados ==="
	@echo "Engine detectada: $(DB_ENGINE)"
ifeq ($(DB_ENGINE),sqlite)
	@echo "Removendo db.sqlite3..."
	@rm -f db.sqlite3 2>/dev/null || true
else
	@echo "PostgreSQL detectado — dropando e recriando banco..."
	@python -c "
import sys
from decouple import config
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    db_name = config('POSTGRES_DB', default='professordash')
    db_user = config('POSTGRES_USER', default='prof')
    db_password = config('POSTGRES_PASSWORD', default='')
    db_host = config('DB_HOST', default='db')
    db_port = config('DB_PORT', default=5432, cast=int)

    conn = psycopg2.connect(
        dbname='template1',
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(f'DROP DATABASE IF EXISTS {db_name}')
    cur.execute(f'CREATE DATABASE {db_name} OWNER {db_user}')
    cur.close()
    conn.close()
    print(f'Banco {db_name} recriado com sucesso.')
except Exception as e:
    print(f'Erro ao resetar banco PostgreSQL: {e}')
    print('Tente manualmente: dropdb && createdb')
    sys.exit(1)
"
endif
	@echo "Rodando migrations..."
	@python manage.py migrate --run-syncdb 2>/dev/null || python manage.py migrate
	@echo ""
	@echo "=== Reset concluído! ==="

seed: ## Cria dados de seed (admin, turmas, alunos, matrículas)
	@echo "=== Criando seed data ==="
	@python manage.py criar_seed_data
	@echo ""
	@echo "=== Seed concluído! ==="

setup: reset seed ## Reset + seed (one command)
	@echo ""
	@echo "=== Setup completo! ==="
	@python manage.py criar_seed_data --dry-run 2>/dev/null || true
	@echo ""
	@echo "Comandos úteis:"
	@echo "  make shell    — abrir Django shell"
	@echo "  make test     — rodar testes"
	@echo "  make server   — iniciar servidor de desenvolvimento"

# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

migrate: ## Aplica migrations pendentes
	python manage.py migrate

shell: ## Abre o shell interativo do Django
	python manage.py shell_plus 2>/dev/null || python manage.py shell

test: ## Roda todos os testes (pytest)
	python -m pytest $(ARGS)

testv: ## Roda testes com verbose
	python -m pytest -v $(ARGS)

server: ## Inicia servidor de desenvolvimento
	python manage.py runserver 0.0.0.0:8000

clean: ## Remove arquivos temporários e bytecode
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "Limpeza concluída."

# ---------------------------------------------------------------------------
# Qualidade de código
# ---------------------------------------------------------------------------

format: ## Formata código com black
	black .

lint: ## Verifica código com ruff
	ruff check . --fix
