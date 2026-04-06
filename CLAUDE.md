# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projeto

**ProfessorDash** — sistema Django para gerenciamento de turmas, aulas, materiais e entregas de alunos. Professor Toni Coimbra, SEED-PR. Domínio: `aulas.tonicoimbra.com`.

## Comandos

```bash
# Ativar ambiente Python
source .venv/bin/activate

# Dev usa SQLite — NÃO precisa de Docker para desenvolver
python manage.py migrate
python manage.py runserver

# Subir PostgreSQL + Redis (só se quiser testar com prod settings)
docker compose up -d db redis

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

Django 5.1 + HTMX 2.x + Alpine.js 3.x + Tailwind CSS 3.x (todos via CDN). PostgreSQL 16 + Redis 7 em produção. Dev: SQLite + cache em memória. Deploy: Docker Compose + Caddy (HTTPS automático). Python 3.12.

### Settings split

`config/settings/` com três módulos: `base.py` (shared), `local.py` (SQLite, debug), `production.py` (PostgreSQL, Redis, HTTPS). pytest.ini aponta para `config.settings.local`. Config usa `python-decouple` para `.env`.

### Apps

| App | Responsabilidade |
|---|---|
| `core` | `BaseModel` (timestamps), mixins de auth, validators de upload, templatetags markdown, context processor `auth_flags` |
| `turmas` | Turma + Matricula. Todo acesso público usa `token_publico` (UUID) |
| `aulas` | Plano de ensino com conteúdo MarkdownxField, ordenação por drag-and-drop |
| `materiais` | Upload (PDF/ZIP/código) + links externos + conteúdo inline Markdown |
| `atividades` | Atividade + Entrega. Status automático: `entregue` vs `atrasada` |
| `avaliacoes` | Apenas templates (boletim, minhas_notas) — sem models/views próprias. Views estão em `turmas/views.py` |
| `alunos` | Aluno + importação CSV. Vinculação ao `User` via Google OAuth |
| `tarefas` | Tarefa + RealizacaoTarefa. Grade de tarefas por turma (checkbox por aluno via HTMX) |

### Google OAuth

Configurado via variáveis de ambiente `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` no `.env` da VPS. Sem elas, o login Google fica indisponível. URI de callback: `https://aulas.tonicoimbra.com/accounts/google/login/callback/`. A função `core.auth.is_google_oauth_configured()` verifica env vars ou SocialApp no banco.

`core/adapters.py` — `SocialAccountAdapter` vincula automaticamente o `User` ao `Aluno` cadastrado com o mesmo e-mail no primeiro login Google (e em logins subsequentes via `pre_social_login`). Isso é o que permite que `AlunoAutenticadoMixin` encontre a matrícula via `aluno__user`.

### URL routing centralizado

Todas as URLs (admin e portal) ficam em `turmas/urls.py` com namespace único `turmas`. É incluído sem prefixo em `config/urls.py` — os prefixos `/painel/turmas/` e `/turma/<uuid:token>/` são definidos internamente. As views de outros apps (aulas, materiais, alunos, atividades) são importadas e registradas ali mesmo. Reverso: `turmas:aulas_lista`, `turmas:portal_aulas_detalhe`, etc.

Dashboard do professor: `core/urls.py` (namespace `core`), acessível em `/painel/`.

### Dois níveis de interface

- `/painel/*` — professor (`is_staff=True`), login próprio (email+senha)
- `/turma/<uuid:token>/*` — aluno (Google OAuth) ou público (sem login)

### Template hierarchy

`templates/base.html` → três layouts derivados:
- `base_admin.html` — painel do professor (`/painel/`)
- `base_publico.html` — portal público da turma (sem login)
- `base_aluno.html` — área do aluno autenticado

### Mixins principais (`core/mixins.py`)

- `ProfessorRequiredMixin` — verifica `request.user.is_staff`
- `TurmaPublicaMixin` — resolve `self.turma` pelo `token` da URL (via `setup()`)
- `AlunoAutenticadoMixin` — herda `TurmaPublicaMixin` + `LoginRequiredMixin`, resolve `self.matricula`

### Fragmentos HTMX

Views que respondem a requests HTMX retornam fragmentos HTML (não página completa). Padrão:

```python
if self.request.htmx:
    return render(request, 'componente/_parcial.html', context)
return render(request, 'pagina_completa.html', context)
```

### Extensões Markdown customizadas (`core/markdown_extensions.py`)

Blocos `:::tipo` são convertidos em componentes HTML ricos pelo `ProfessorDashPreprocessor`. Tipos suportados:

- Callouts: `:::objetivo`, `:::importante`, `:::dica`, `:::exemplo`, `:::atencao`, `:::conceito`, `:::exercicio`, `:::curiosidade`
- `:::roteiro` — notas de fala do professor (ocultas no modo aluno)
- `:::resumo` — lista de tópicos com checkmarks
- `:::questao Enunciado?` — questão de múltipla escolha com alternativas (`a) Texto *` para marcar correta) e gabarito (linha `> Explicação`)

O templatetag `|markdownify` (em `core/templatetags/markdownx.py`) strip frontmatter YAML antes de renderizar. Carregado com `{% load markdownx %}`.

### Third-party libs relevantes

- **django-allauth** — Google OAuth para alunos
- **markdownx** — editor/preview de Markdown nos campos de aula
- **whitenoise** — serve static files em produção (sem Nginx)
- **django-import-export** — import/export de dados no admin
- **python-decouple** — `.env` config management

### Test fixtures (`conftest.py`)

Fixtures globais disponíveis em todos os testes: `professor` (is_staff), `aluno_user`, `aluno`, `turma`, `matricula`, `atividade_aberta`, `client_professor`, `client_aluno`, `client_aluno_sem_matricula`. Usar estas fixtures ao escrever novos testes.

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
