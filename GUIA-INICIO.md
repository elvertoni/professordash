# Guia de Início do Projeto — ProfessorDash
**Linux Mint · Antigravity · Multi-provider AI**

---

## Pré-requisitos

```bash
# Verificar o que já está instalado
python3 --version        # >= 3.12
docker --version         # >= 26
docker compose version   # >= 2.x
git --version
node --version           # opcional, só se usar Tailwind CLI
```

Instalar Antigravity (se ainda não tiver):
```bash
pip install antigravity
```

---

## Etapa 0 — Estrutura Local

### 0.1 Criar e entrar na pasta do projeto
```bash
mkdir professordash && cd professordash
```

### 0.2 Ambiente Python isolado
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install django djangorestframework django-allauth \
            django-markdownx django-import-export \
            psycopg2-binary redis python-decouple \
            gunicorn whitenoise python-magic pillow weasyprint \
            pytest pytest-django black ruff
pip freeze > requirements/base.txt
```

### 0.3 Criar projeto Django
```bash
pip install django
django-admin startproject config .
python manage.py startapp core
python manage.py startapp turmas
python manage.py startapp aulas
python manage.py startapp materiais
python manage.py startapp atividades
python manage.py startapp avaliacoes
python manage.py startapp alunos
```

### 0.4 Subir para o GitHub
```bash
# Criar .gitignore antes
curl -o .gitignore https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore
echo ".env" >> .gitignore
echo "media/" >> .gitignore

git init
git add .
git commit -m "chore: estrutura inicial do projeto"
git branch -M main
git remote add origin https://github.com/<seu-usuario>/professordash.git
git push -u origin main
```

---

## Etapa 1 — Setup de IA Multi-provider

### Por que multi-provider?
Evitar lock-in em um único modelo. A ideia é usar o melhor modelo para cada tipo de tarefa e ter fallback caso um provider esteja fora ou com limitações.

### Mapeamento de providers por tarefa

| Tarefa | Provider Principal | Fallback |
|---|---|---|
| Geração de código Django | Claude Sonnet (claude code) | Gemini 2.5 Pro |
| Frontend (templates + Tailwind) | Claude Sonnet | GPT-4o |
| Revisão de código / PR review | Gemini 2.5 Pro | Claude |
| Geração de testes | Claude Sonnet | Gemini |
| Debugging pontual | Qualquer (via Antigravity) | — |
| Documentação | Claude | Gemini |

### Configurar Antigravity com múltiplos providers
```bash
# ~/.config/antigravity/config.toml (exemplo)
[providers]
default = "claude"

[providers.claude]
api_key = "$ANTHROPIC_API_KEY"
model   = "claude-sonnet-4-5"

[providers.gemini]
api_key = "$GEMINI_API_KEY"
model   = "gemini-2.5-pro"

[providers.openai]
api_key = "$OPENAI_API_KEY"
model   = "gpt-4o"
```

> **Dica**: Nunca commite chaves. Use `$VARIAVEL` no config e exporte no `.bashrc`/`.zshrc`.

---

## Etapa 2 — Documentação do Projeto (para os agentes)

Peça para o agente gerar a documentação **com base apenas no que já existe**:

```
Crie uma pasta docs/ na raiz do projeto com toda a documentação
necessária para que qualquer pessoa entenda os guidelines e padrões.
Separe em arquivos .md e crie um docs/README.md como índice.
Não documente nada além do que já existe. Use @PRD.md como referência.
Seja simples e direto.
```

Estrutura esperada:
```
docs/
├── README.md          ← índice geral
├── arquitetura.md     ← stack, fluxo de request, diagrama
├── modelos.md         ← entidades e relacionamentos
├── autenticacao.md    ← professor vs aluno vs público
├── deploy.md          ← Docker + Caddy + VPS
└── convencoes.md      ← padrões de código, commits, branches
```

---

## Etapa 3 — CLAUDE.md (contexto para Claude Code)

```
/init com base na estrutura inicial do projeto, no @PRD.md
e na documentação @docs/README.md, gere o CLAUDE.md
```

O `CLAUDE.md` deve conter:
- Stack resumida
- Estrutura de apps
- Convenções de código (Black, Ruff, CBV)
- Como rodar localmente
- Como rodar os testes
- Providers de IA disponíveis no projeto

---

## Etapa 4 — Agentes de IA

```
Baseado em @docs/README.md e @PRD.md, crie uma pasta agents/
com agentes especializados em cada função do time de desenvolvimento.
Coloque cada agente em um .md separado.
Crie agents/README.md como índice com descrição de quando usar cada um.

Regras:
- Agentes de código Django: usar MCP context7 para código atualizado
- Agente de testes: usar MCP playwright para verificar o sistema
- Criar apenas agentes necessários para produção de código
```

Agentes sugeridos para este projeto:

| Arquivo | Responsabilidade |
|---|---|
| `agents/backend.md` | Models, views, forms, URLs Django |
| `agents/frontend.md` | Templates DTL + Tailwind + HTMX + Alpine |
| `agents/auth.md` | django-allauth, Google OAuth, permissões |
| `agents/devops.md` | Docker, Caddy, VPS, deploy, backup |
| `agents/qa.md` | pytest-django + playwright, cobertura |

---

## Etapa 5 — TASKS.md

Gere o arquivo de tarefas para controle das sprints:

```
Com base no @PRD.md e no @SPEC.md, gere um TASKS.md na raiz do projeto
com todas as sprints e sub-tarefas do MVP. Use checkboxes [ ] para cada
sub-tarefa. Organize por Sprint 0, Sprint 1, Sprint 2, Sprint 3, Sprint 4.
```

Formato esperado:
```markdown
## Sprint 0 — Setup [ ]
- [ ] 0.1 Estrutura Django + apps
- [ ] 0.2 Docker Compose (app + postgres + redis)
- [ ] 0.3 Caddy config + subdomínio
- [ ] 0.4 django-allauth Google OAuth
- [ ] 0.5 Deploy inicial na VPS
```

Para executar uma tarefa específica:
```
Execute a tarefa 0.3 da sprint 0 em @TASKS.md.
Execute somente tarefas ainda não concluídas (sem X).
Use os agentes necessários para cada sub-tarefa.
Após concluir cada sub-tarefa, marque X no @TASKS.md.
```

---

## Etapa 6 — Gestão de Contexto (boas práticas)

| Situação | Comando |
|---|---|
| Nova sprint ou tarefa sem relação com a anterior | `/clear` |
| Continuando tarefa relacionada | `/compact` |
| Trocando de agente/provider | `/clear` + novo contexto |
| Bug que surgiu no meio de outra tarefa | Abrir nova sessão, referenciar o arquivo específico |

### Dica: contexto mínimo por sessão
Ao iniciar uma sessão de trabalho, forneça sempre:
```
Contexto: @CLAUDE.md @TASKS.md @apps/<app-relevante>/models.py
Tarefa: <descrição clara e curta>
```
Não jogue todos os arquivos no contexto — só o que é necessário para a tarefa atual.

---

## Etapa 7 — Rodando Localmente

```bash
# Subir banco e redis via Docker, Django local
docker compose -f docker-compose.dev.yml up -d db redis

# Migrations e superuser
python manage.py migrate
python manage.py createsuperuser

# Rodar o servidor
python manage.py runserver

# Rodar testes
pytest
```

---

## Ordem de Execução Resumida

```
0.1  mkdir + venv + pip install
0.2  django-admin startproject + startapp (7 apps)
0.3  git init + push GitHub
1.0  Gerar docs/ (prompt Claude)
2.0  /init → CLAUDE.md
3.0  Gerar agents/ (prompt Claude)
4.0  Gerar TASKS.md (prompt Claude)
5.0  Executar sprints via TASKS.md
```

---

*Versão 1.0 — Março 2026*
