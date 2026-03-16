# TASKS.md — ProfessorDash MVP

Referência: `PRD.md` (funcionalidades) + `SPEC.md` (técnico).
Agente responsável por cada tarefa: ver `agents/README.md`.

---

## Sprint 0 — Setup [ ]

> Objetivo: projeto rodando localmente e na VPS com autenticação funcional.

- [x] 0.1 Configurar `settings/` com `base.py`, `local.py`, `production.py` (python-decouple + `.env`)
- [x] 0.2 Configurar `DATABASES` (PostgreSQL), `CACHES` (Redis sessão), `MEDIA_ROOT`, `STATIC_ROOT`
- [x] 0.3 Criar `apps/core/models.py` com `BaseModel` (timestamps `criado_em`, `atualizado_em`)
- [x] 0.4 Criar `apps/core/mixins.py` com `ProfessorRequiredMixin`, `TurmaPublicaMixin`, `AlunoAutenticadoMixin`
- [x] 0.5 Criar `apps/core/validators.py` com `validar_arquivo()` e listas de MIME types permitidos
- [x] 0.6 Configurar django-allauth (Google OAuth2): `INSTALLED_APPS`, `SOCIALACCOUNT_PROVIDERS`, URLs
- [x] 0.7 Criar `templates/base.html`, `base_admin.html`, `base_aluno.html`, `base_publico.html`
- [x] 0.8 Criar `templates/components/_sidebar.html` e `_messages.html`
- [x] 0.9 Criar `static/js/app.js` com Alpine stores: `sidebar`, `tabs`, `confirm`
- [x] 0.10 Criar `docker/Dockerfile`, `docker/entrypoint.sh`, `docker/caddy/Caddyfile`
- [x] 0.11 Criar `docker-compose.yml` (dev) e `docker-compose.prod.yml` com serviços `app`, `db`, `redis`, `caddy`
- [x] 0.12 Criar `.env.example` com todas as variáveis documentadas
- [x] 0.13 Configurar `requirements/base.txt`, `local.txt`, `production.txt`
- [x] 0.14 Criar `config/urls.py` com rota `/entrar/`, `/sair/`, `/accounts/`, `/painel/`, `/turma/`
- [ ] 0.15 Deploy inicial na VPS: subir `docker-compose.prod.yml`, verificar HTTPS no domínio

---

## Sprint 1 — Core Admin [ ]

> Objetivo: professor consegue criar turmas, aulas e materiais. Aluno acessa via link público.

### Turmas

- [x] 1.1 Criar `turmas.Turma` e `turmas.Matricula` (models conforme `SPEC.md` 4.3–4.4)
- [x] 1.2 Criar views: `TurmaListView`, `TurmaCreateView`, `TurmaDetailView`, `TurmaUpdateView`
- [x] 1.3 Criar view `TurmaArquivarView` (toggle `ativa=False`)
- [x] 1.4 Criar view `TurmaPortalPublicoView` — acesso via `token_publico` sem login
- [x] 1.5 Criar `TurmaForm` com campos: nome, código, período, ano letivo, descrição
- [x] 1.6 Criar templates: `turmas/lista.html`, `turmas/detalhe.html`, `turmas/form.html`, `turmas/portal.html`
- [x] 1.7 Adicionar `_card_turma.html` como componente reutilizável
- [x] 1.8 Escrever `turmas/urls.py` com todas as rotas do painel e portal público

### Aulas

- [x] 1.9 Criar `aulas.Aula` (model conforme `SPEC.md` 4.5)
- [x] 1.10 Criar views: `AulaListView`, `AulaCreateView`, `AulaUpdateView`, `AulaDeleteView`
- [x] 1.11 Criar `AulaReordenarView` (HTMX POST, salva campo `ordem` via drag-and-drop)
- [x] 1.12 Criar `AulaMarcarRealizadaView` (HTMX toggle `realizada`)
- [x] 1.13 Criar `AulaForm` com `MarkdownxField` para `conteudo`
- [x] 1.14 Criar templates: `aulas/lista.html`, `aulas/detalhe.html`, `aulas/form.html`
- [x] 1.15 Criar template público `aulas/lista_publica.html` e `aulas/detalhe_publico.html`

### Materiais

- [ ] 1.16 Criar `materiais.Material` com choices `TipoMaterial` e `VisibilidadeMaterial` (model conforme `SPEC.md` 4.6)
- [ ] 1.17 Criar views: `MaterialListView`, `MaterialCreateView`, `MaterialUpdateView`, `MaterialDeleteView`
- [ ] 1.18 Criar `MaterialForm` com campos condicionais por tipo (arquivo, url_externa, conteudo_md)
- [ ] 1.19 Validar upload em `MaterialForm.clean_arquivo()` usando `validar_arquivo()`
- [ ] 1.20 Criar template `materiais/form.html` com Alpine.js para mostrar/ocultar campos por tipo
- [ ] 1.21 Criar template público `materiais/lista_publica.html` respeitando `visibilidade`
- [ ] 1.22 Criar `_card_material.html` como componente

---

## Sprint 2 — Atividades e Entregas [ ]

> Objetivo: aluno consegue visualizar atividades e enviar entregas. Professor visualiza e baixa em ZIP.

### Atividades

- [ ] 2.1 Criar `atividades.Atividade` com choices `TipoEntrega` (model conforme `SPEC.md` 4.7)
- [ ] 2.2 Criar `atividades.Entrega` com choices `StatusEntrega` (model conforme `SPEC.md` 4.8)
- [ ] 2.3 Criar views admin: `AtividadeListView`, `AtividadeCreateView`, `AtividadeUpdateView`, `AtividadeDeleteView`
- [ ] 2.4 Criar `AtividadeDetailView` com lista de entregas (quem entregou / quem não entregou)
- [ ] 2.5 Criar `AtividadeForm` com `MarkdownxField` para `descricao`
- [ ] 2.6 Criar template `atividades/detalhe.html` com `_tabela_entregas.html` como componente
- [ ] 2.7 Criar `_card_atividade.html` como componente

### Entregas

- [ ] 2.8 Criar `EntregarAtividadeView` (aluno): verificar matricula, prazo, reenvio permitido
- [ ] 2.9 Criar `EntregaForm` com campos condicionais por `tipo_entrega` (arquivo, texto, link)
- [ ] 2.10 Calcular `status` automaticamente no save: `ENTREGUE` se dentro do prazo, `ATRASADA` se fora
- [ ] 2.11 Validar upload de entrega em `EntregaForm.clean_arquivo()` com `validar_arquivo()`
- [ ] 2.12 Criar template `atividades/entregar.html` com Alpine.js para campos condicionais
- [ ] 2.13 Criar `DownloadEntregasZipView`: gerar ZIP com arquivos nomeados por `slugify(aluno.nome)`
- [ ] 2.14 Criar `ReabrirPrazoAlunoView`: professor redefine prazo para aluno específico
- [ ] 2.15 Criar templates públicos de listagem de atividades (somente visualização sem login)

### Alunos

- [ ] 2.16 Criar `alunos.Aluno` (model conforme `SPEC.md` 4.2)
- [ ] 2.17 Criar `apps/alunos/signals.py` com `post_social_login`: vincular/criar `Aluno` pelo email Google
- [ ] 2.18 Criar views admin: `AlunoListView`, `AlunoDetailView`, `AlunoCreateView`, `AlunoUpdateView`
- [ ] 2.19 Criar `AlunoImportarCSVView` com django-import-export
- [ ] 2.20 Criar `AlunoMoverTurmaView` (transferir matrícula)
- [ ] 2.21 Criar `MinhaAreaView` (aluno): resumo das atividades, status de entregas

---

## Sprint 3 — Notas e Boletim [ ]

> Objetivo: professor lança notas, aluno vê suas notas, boletim exportável.

- [ ] 3.1 Criar `AvaliarEntregaView` (HTMX): inline edit de nota (0–10) + feedback textual
- [ ] 3.2 Criar template `avaliacoes/_inline_avaliacao.html` — fragmento retornado pelo HTMX
- [ ] 3.3 Criar `BoletimTurmaView`: grid aluno × atividade com notas e médias calculadas
- [ ] 3.4 Criar `ExportarBoletimCSVView`: CSV com header `[Aluno, Matrícula, atividades..., Média]`
- [ ] 3.5 Criar `ExportarBoletimPDFView`: gerar PDF com WeasyPrint a partir do template HTML
- [ ] 3.6 Criar template `avaliacoes/boletim.html` com `_boletim_grid.html` como componente
- [ ] 3.7 Criar `MinhasNotasView` (aluno): ver próprias notas e feedback por atividade
- [ ] 3.8 Criar template `avaliacoes/minhas_notas.html`

---

## Sprint 4 — Dashboard e Polimento [ ]

> Objetivo: dashboard funcional, import CSV, responsividade, testes e deploy estável.

### Dashboard

- [ ] 4.1 Criar `DashboardView` (professor): KPIs — turmas ativas, total alunos, atividades abertas
- [ ] 4.2 Criar `_htmx_feed_view`: feed de entregas das últimas 24h (fragmento HTMX com polling)
- [ ] 4.3 Criar `_htmx_stats_turma_view`: estatísticas por turma (taxa de entrega, média)
- [ ] 4.4 Criar alertas no dashboard: atividades próximas do prazo, entregas não avaliadas
- [ ] 4.5 Criar template `core/dashboard.html` com cards de KPI e feed lateral

### Polimento

- [ ] 4.6 Revisar todos os templates para responsividade mobile-first (breakpoints `sm:`, `md:`)
- [ ] 4.7 Criar `templates/components/_modal_confirm.html` e integrar em todas as exclusões
- [ ] 4.8 Criar `templates/components/_empty_state.html` para listas vazias
- [ ] 4.9 Adicionar paginação em listagens com muitos registros (alunos, entregas)
- [ ] 4.10 Adicionar busca ao vivo de alunos via HTMX em `TurmaAlunos`

### Testes

- [ ] 4.11 Criar `conftest.py` com fixtures: `professor`, `aluno`, `turma`, `matricula`, `atividade_aberta`
- [ ] 4.12 Escrever testes para fluxo de entrega (`test_entrega_flow.py`)
- [ ] 4.13 Escrever testes para acesso público vs restrito por `token_publico`
- [ ] 4.14 Escrever testes para `validar_arquivo()` (tipos permitidos e bloqueados)
- [ ] 4.15 Verificar cobertura mínima de 60% nas views críticas (`pytest --cov`)

### Deploy Final

- [ ] 4.16 Configurar cron de backup na VPS (`/etc/cron.d/professordash-backup`)
- [ ] 4.17 Verificar checklist de segurança completo (ver `docs/deploy.md`)
- [ ] 4.18 Validar fluxos completos com Playwright: login professor, criar turma, enviar entrega, lançar nota
- [ ] 4.19 Validar responsividade no mobile (Playwright com viewport reduzido)

---

## Como executar uma tarefa

```
Execute a tarefa 1.1 da sprint 1 em @TASKS.md.
Execute somente tarefas ainda não concluídas (sem X no checkbox).
Use o agente em @agents/backend.md para implementar.
Após concluir, marque [x] no @TASKS.md.
```

Marcar como concluída: substituir `[ ]` por `[x]`.
