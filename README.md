# ProfessorDash

Sistema Django para gerenciamento de turmas, aulas, materiais e entregas de alunos do Curso Técnico em Desenvolvimento de Sistemas (Professor Toni Coimbra, SEED-PR). Domínio de produção: `aulas.tonicoimbra.com`.

## Stack

Django 5.1 + HTMX + Alpine.js + Tailwind CSS. PostgreSQL 16 + Redis 7 em produção; SQLite em desenvolvimento. Deploy via Docker Compose + Caddy.

## Desenvolvimento

```bash
source .venv/bin/activate
python manage.py migrate
python manage.py runserver
```

Testes com `pytest`. Formatação com `black .` e lint com `ruff check . --fix`.

## Formato de aulas

O formato canônico das aulas em Markdown — modos conceitual, prático e apostila — está definido em **[FORMATO_AULAS.md](FORMATO_AULAS.md)**. É a fonte de verdade para todos os geradores (Claude, Hermes Agent, CoimbraBot) e para o renderer do ProfessorDash. Antes de gerar ou editar uma aula, consulte esse documento.

Os arquivos `AULAS_SPEC.md` e `formato_ideal.md` foram deprecados e apenas redirecionam para `FORMATO_AULAS.md`.

## Documentação

Documentação completa em [`docs/`](docs/README.md): arquitetura, modelos, autenticação, deploy e convenções.
