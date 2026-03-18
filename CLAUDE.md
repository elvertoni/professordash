# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projeto

**ProfessorDash** — sistema Django para gerenciamento de turmas, aulas, materiais e entregas de alunos. Professor Toni Coimbra, SEED-PR. Domínio: `aulas.tonicoimbra.com`.

## Comandos

```bash
# Ativar ambiente Python
source .venv/bin/activate

# Subir banco e Redis (Django roda local)
docker compose up -d db redis

# Migrations e superuser
python manage.py migrate
python manage.py createsuperuser

# Servidor de desenvolvimento
python manage.py runserver

# Testes
pytest
pytest turmas/                             # testar um app específico
pytest -k "test_entrega"                   # testar por nome
pytest --cov=. --cov-report=html           # com cobertura

# Qualidade de código
black .
ruff check . --fix
```

## Arquitetura

### Stack

Django 5.1 + HTMX 2.x + Alpine.js 3.x + Tailwind CSS 3.x (todos via CDN). PostgreSQL 16 + Redis 7. Deploy: Docker Compose + Caddy (HTTPS automático). Python 3.12.

### Apps

| App | Responsabilidade |
|---|---|
| `core` | `BaseModel` (timestamps), mixins de auth, validators de upload, templatetags markdown |
| `turmas` | Turma + Matricula. Todo acesso público usa `token_publico` (UUID) |
| `aulas` | Plano de ensino com conteúdo MarkdownxField, ordenação por drag-and-drop |
| `materiais` | Upload (PDF/ZIP/código) + links externos + conteúdo inline Markdown |
| `atividades` | Atividade + Entrega. Status automático: `entregue` vs `atrasada` |
| `avaliacoes` | Nota + feedback por Entrega. Export boletim CSV (WeasyPrint para PDF) |
| `alunos` | Aluno + importação CSV. Vinculação ao `User` via Google OAuth |

### Módulos auxiliares

| Módulo | Responsabilidade |
|---|---|
| `gerador_aulas/` | Extratores de conteúdo (PDF, PPTX, DOCX, URL, RCO) + geração de aulas via IA (OpenRouter). Uso exclusivo do professor/admin. Ver `gerador_aulas/PRD-GeradorAulas-v2.md` |

### Dois níveis de interface

- `/painel/*` — professor (`is_staff=True`), login próprio (email+senha)
- `/turma/<uuid:token>/*` — aluno (Google OAuth) ou público (sem login)

### Mixins principais (`core/mixins.py`)

- `ProfessorRequiredMixin` — verifica `request.user.is_staff`
- `TurmaPublicaMixin` — resolve `self.turma` pelo `token` da URL
- `AlunoAutenticadoMixin` — herda os dois acima, verifica `Matricula` ativa

### Fragmentos HTMX

Views que respondem a requests HTMX retornam fragmentos HTML (não página completa). Padrão:

```python
if self.request.htmx:
    return render(request, 'componente/_parcial.html', context)
return render(request, 'pagina_completa.html', context)
```

## Convenções

- **Views**: sempre CBV (Class-Based Views)
- **Forms**: toda validação no Django Form, nunca só no JS
- **Queries**: `select_related` / `prefetch_related` obrigatórios em listagens
- **Commits**: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`, `test:`
- **Branches**: `main` (produção), `dev` (desenvolvimento), `feature/<nome>`
- **Testes**: pytest-django, cobertura mínima 60% nas views críticas

## Documentação Completa

Ver `docs/`:

- `docs/arquitetura.md` — stack detalhada, infraestrutura, diagrama
- `docs/modelos.md` — modelos Django com campos e relacionamentos
- `docs/autenticacao.md` — fluxo Google OAuth, mixins, acesso público
- `docs/deploy.md` — Dockerfile, docker-compose, Caddy, backup, .env
- `docs/convencoes.md` — padrões de código, Git, testes, templates, HTMX
