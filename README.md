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

### Integração via API

O ProfessorDash expõe uma API REST para importação automática de aulas em Markdown, projetada para integração com o **Hermes Agent**, **Claude Desktop** ou scripts personalizados. Consulte:

- **[docs/api.md](docs/api.md)** — documentação da API de importação (endpoint, autenticação via token, exemplos com `curl`, Python e Hermes)
- **[scripts/hermes_importar.sh](scripts/hermes_importar.sh)** — script wrapper bash para chamar a API via SSH/VPS
