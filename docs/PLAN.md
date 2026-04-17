# PLAN.md — Auditoria Funcional e UI/UX do ProfessorDash

## Contexto

Sistema Django 5.1 para gerenciamento de turmas de um professor da SEED-PR.
Stack: Python 3.12 · HTMX 2.x · Alpine.js 3.x · Tailwind CSS 3.x (CDN) · SQLite (dev) · PostgreSQL (prod).

---

## Objetivos da Auditoria

| # | Objetivo |
|---|---|
| 1 | Identificar rotas/views quebradas ou mal configuradas |
| 2 | Detectar inconsistências visuais e problemas de acessibilidade nos templates |
| 3 | Verificar interações HTMX (fragmentos, targets, erros silenciosos) |
| 4 | Apontar queries N+1 ou sem `select_related`/`prefetch_related` |
| 5 | Mapear lacunas de cobertura de testes nas views críticas |

---

## Fases

### Fase 1 — Mapeamento (explorer-agent)

**Responsável:** `explorer-agent`
**Entradas:** `turmas/urls.py`, `config/urls.py`, `templates/`
**Saída:** relatório de rotas e templates mapeados

#### Checklist

- [ ] Listar todas as 60+ rotas registradas em `turmas/urls.py` (namespace `turmas`)
- [ ] Confirmar que cada `name=` tem um template correspondente e que o `reverse()` não quebra
- [ ] Identificar views importadas em `turmas/urls.py` que podem estar faltando (`aulas_views`, `materiais_views`, `alunos_views`, `atividades_views`, `tarefas_views`)
- [ ] Mapear os dois níveis de interface: `/painel/*` (professor `is_staff`) e `/turma/<uuid:token>/*` (aluno/público)
- [ ] Verificar rotas públicas sem autenticação que exponham dados sensíveis
- [ ] Confirmar que `core/urls.py` (namespace `core`) está incluído em `config/urls.py` e que `/painel/` resolve corretamente
- [ ] Listar templates órfãos (existem em `templates/` mas não são referenciados por nenhuma view)
- [ ] Listar templates ausentes (referenciados em views mas sem arquivo correspondente)
- [ ] Verificar hierarquia de herança: `base.html` → `base_admin.html` / `base_publico.html` / `base_aluno.html`
- [ ] Verificar fragmentos HTMX com underscore (`_card_atividade.html`, `_checkbox.html`, etc.) e confirmar que as views usam `if self.request.htmx` para retorná-los

---

### Fase 2 — Frontend (frontend-specialist)

**Responsável:** `frontend-specialist`
**Entradas:** `templates/`, `static/`, `base.html`, `base_admin.html`, `base_publico.html`, `base_aluno.html`
**Saída:** lista priorizada de problemas UI/UX com localização exata (arquivo + linha)

#### Checklist — Tailwind / Layout

- [ ] Verificar responsividade nos templates de listagem (`turmas/lista.html`, `aulas/lista.html`, `atividades/lista.html`)
- [ ] Consistência de cores e espaçamento nos cards (`components/_card_turma.html`, `atividades/_card_atividade.html`, `materiais/_card_material.html`)
- [ ] Sidebar (`components/_sidebar.html`): links ativos destacados, colapso mobile
- [ ] Empty states (`components/_empty_state.html`): presença em todas as listagens que podem retornar zero resultados
- [ ] Modal de confirmação (`components/_modal_confirm.html`): uso consistente antes de ações destrutivas (excluir turma, remover aluno)
- [ ] Mensagens de feedback (`components/_messages.html`): presença no `base_admin.html` e `base_publico.html`
- [ ] `avaliacoes/boletim.html` e `avaliacoes/boletim_pdf.html`: layout de tabela em tela pequena

#### Checklist — HTMX

- [ ] `tarefas/_checkbox.html` — toggle via HTMX: `hx-post`, `hx-target`, `hx-swap` corretos; resposta retorna apenas o fragmento
- [ ] `tarefas/_editar_form.html` — edição inline: `hx-put`/`hx-post`, indicador de loading
- [ ] `tarefas/_tarefa_header.html` — cabeçalho editável inline
- [ ] `aulas/_aula_item.html` — drag-and-drop (reordenar): `hx-post` para `turmas:aulas_reordenar`; verificar `hx-trigger` e `hx-include`
- [ ] `alunos/lista.html` + `alunos/_tabela_alunos.html` — busca HTMX (`turmas:alunos_busca_htmx`): debounce, `hx-target` correto
- [ ] `alunos/_email_feedback.html` — fragmento de feedback de e-mail
- [ ] `avaliacoes/_inline_avaliacao.html` — lançamento de nota inline
- [ ] `core/dashboard.html` — feed de entregas recentes: `hx-get`, polling ou trigger correto
- [ ] Verificar que todas as views que respondem a HTMX têm o padrão `if self.request.htmx: return render(...)` e não retornam página completa
- [ ] Verificar tratamento de erro HTMX: status HTTP não-200 exibe mensagem ao usuário (sem falha silenciosa)

#### Checklist — Acessibilidade

- [ ] Todos os `<img>` possuem `alt`
- [ ] Inputs de formulário têm `<label>` associado ou `aria-label`
- [ ] Botões de ação têm texto descritivo ou `aria-label` (não apenas ícone)
- [ ] Contraste de cores suficiente (texto sobre fundo colorido nos callouts Markdown)
- [ ] Foco visível em elementos interativos (não removido com `outline-none` sem alternativa)
- [ ] Tabelas do boletim têm `<th scope="col/row">`

---

### Fase 3 — Backend (backend-specialist)

**Responsável:** `backend-specialist`
**Entradas:** `*/views.py`, `*/models.py`, `*/forms.py`, `core/mixins.py`, `core/adapters.py`
**Saída:** lista de bugs, riscos de segurança e oportunidades de otimização

#### Checklist — Mixins e Autenticação

- [ ] `ProfessorRequiredMixin`: todos os `/painel/*` views herdam corretamente; nenhuma view de escrita exposta sem `is_staff`
- [ ] `TurmaPublicaMixin`: `self.turma` resolvido via `token` no `setup()`; 404 adequado para token inválido
- [ ] `AlunoAutenticadoMixin`: `self.matricula` resolvido; aluno sem matrícula na turma recebe 403/redirect correto
- [ ] `core/adapters.py` (`SocialAccountAdapter`): vinculação automática `User → Aluno` por e-mail funciona em primeiro login e em `pre_social_login`
- [ ] `turmas:entrar` — fluxo de entrada pública na turma: idempotente, não duplica `Matricula`

#### Checklist — Views e Forms

- [ ] `atividades/views.py` — `EntregarAtividadeView`: valida prazo server-side (não só no template); status `entregue` vs `atrasada` definido corretamente
- [ ] `atividades/views.py` — `AvaliarEntregaView`: protege contra notas fora do intervalo válido
- [ ] `atividades/views.py` — `ReabrirPrazoAlunoView`: apenas professor pode reabrir; log de ação
- [ ] `materiais/views.py` — `MaterialCreateView`/`MaterialUpdateView`: validação de MIME via `core/validators.py`; rejeitar `.exe`, `.sh`, etc.
- [ ] `alunos/views.py` — `AlunoImportarCSVView`: encoding UTF-8 e tratamento de linhas malformadas
- [ ] `alunos/views.py` — `AlunoImportarMultiturmaCSVView`: validação de turmas existentes antes de criar matrículas
- [ ] `turmas/views.py` — `BoletimTurmaView` / `ExportarBoletimPDFView`: evitar timeout em turmas grandes
- [ ] `aulas/views.py` — `AulasSincronizarGithubView` e `atividades/views.py` — `AtividadesSincronizarGithubView`: tratamento de erro de rede/API GitHub; não propagar 500 para o usuário
- [ ] `tarefas/views.py` — `TarefaToggleView`: idempotência do toggle (duplo clique não duplica `RealizacaoTarefa`)
- [ ] Verificar uso de `get_object_or_404` vs `get()` direto que pode lançar `DoesNotExist`
- [ ] Verificar CSRF em todas as views POST que não são HTMX puro

#### Checklist — Queries N+1

- [ ] `turmas/views.py` `TurmaDetailView.get_context_data`: aulas, materiais, alunos carregados com `prefetch_related`
- [ ] `turmas/views.py` `BoletimTurmaView.get_context_data`: matrículas + alunos + atividades + entregas
- [ ] `atividades/views.py` `AtividadeDetailView`: entregas com `select_related('aluno__user')`
- [ ] `tarefas/views.py` `TarefasGradeView`: grade com `prefetch_related('realizacoes', 'tarefas')`
- [ ] `alunos/views.py` `AlunoListView`: `select_related('user')` nas listagens
- [ ] `core/views.py` (dashboard): feed de entregas recentes sem N+1 por turma

#### Checklist — Modelos

- [ ] `BaseModel` em `core/models.py`: `created_at`/`updated_at` presentes em todos os models críticos
- [ ] `Entrega`: `status` automático calculado corretamente (property ou signal); não depende de chamada manual
- [ ] `Turma.token_publico`: campo UUID com `default=uuid.uuid4`, `unique=True`, não editável
- [ ] Índices de banco adequados em campos de filtro frequente (`turma`, `aluno`, `status`)

---

### Fase 4 — Testes (test-engineer)

**Responsável:** `test-engineer`
**Entradas:** `*/tests/`, `conftest.py`, `pytest.ini`
**Saída:** relatório de cobertura atual + lista de testes a criar (priorizados)

#### Estado Atual

- Os diretórios `atividades/tests/` e `aulas/tests/` existem mas estão **vazios** (apenas `__pycache__`)
- Nenhum arquivo `conftest.py` encontrado na raiz do projeto
- Cobertura efetiva: **0%** nas views

#### Checklist — Infraestrutura de Testes

- [ ] Criar `conftest.py` na raiz com fixtures padrão definidas no `agents/qa.md`:
  `professor`, `aluno_user`, `aluno`, `turma`, `matricula`, `atividade_aberta`,
  `client_professor`, `client_aluno`, `client_aluno_sem_matricula`
- [ ] Confirmar `pytest.ini` aponta para `config.settings.local` (SQLite, sem Docker)
- [ ] Garantir que `pytest` roda sem erro de configuração: `python manage.py check --deploy` não exigido em local

#### Checklist — Testes Prioritários (views críticas)

**Prioridade 1 — Atividades (`atividades/tests/test_views.py`)**
- [ ] `EntregarAtividadeView`: entrega dentro do prazo → status `entregue`
- [ ] `EntregarAtividadeView`: entrega fora do prazo → status `atrasada`
- [ ] `EntregarAtividadeView`: aluno sem matrícula → 403/redirect
- [ ] `EntregarAtividadeView`: reenvio antes do prazo → atualiza entrega existente
- [ ] `AvaliarEntregaView`: professor lança nota → salvo corretamente
- [ ] `AvaliarEntregaView`: não-professor → 302 redirect
- [ ] `ReabrirPrazoAlunoView`: professor reabre prazo → `prazo_reaberto=True`
- [ ] `DownloadEntregasZipView`: turma sem entregas → resposta válida (zip vazio ou 404)

**Prioridade 2 — Turmas/Boletim (`turmas/tests/test_views.py`)**
- [ ] `TurmaListView`: professor vê suas turmas; anônimo → redirect login
- [ ] `TurmaPortalPublicoView`: token válido → 200; token inválido → 404
- [ ] `TurmaEntrarView`: aluno autenticado sem matrícula → cria matrícula; com matrícula → idempotente
- [ ] `BoletimTurmaView`: professor vê boletim; aluno → 302
- [ ] `ExportarBoletimCSVView`: CSV com header correto e dados de alunos

**Prioridade 3 — Materiais (`materiais/tests/test_views.py`)**
- [ ] `MaterialCreateView`: upload PDF válido → 302 + objeto criado
- [ ] `MaterialCreateView`: upload `.exe` → 200 + erro no form
- [ ] `MaterialDownloadPublicoView`: material existente → 200 com Content-Disposition
- [ ] `MaterialListaPublicaView`: token válido → lista materiais da turma

**Prioridade 4 — Alunos (`alunos/tests/test_views.py`)**
- [ ] `AlunoImportarCSVView`: CSV válido → alunos criados e matriculados
- [ ] `AlunoImportarCSVView`: CSV com e-mail duplicado → comportamento definido (atualizar ou ignorar)
- [ ] `AlunoEmailFeedbackView`: HTMX request → retorna fragmento; não-HTMX → 400 ou redirect

**Prioridade 5 — Tarefas (`tarefas/tests/test_views.py`)**
- [ ] `TarefaToggleView`: professor marca tarefa → `RealizacaoTarefa` criada
- [ ] `TarefaToggleView`: duplo click → toggle correto (cria/remove)
- [ ] `TarefasGradePublicaView`: acesso público (sem login) → 200 somente leitura
- [ ] `TarefasGradeView`: aluno tenta acessar `/painel/` → 302

**Prioridade 6 — Aulas (`aulas/tests/test_views.py`)**
- [ ] `AulaReordenarView`: POST com nova ordem → salva `ordem` corretamente
- [ ] `AulaMarcarRealizadaView`: toggle `realizada` → atualiza campo
- [ ] `AulaDetalhePublicoView`: token válido + aula da turma → 200; aula de outra turma → 404

#### Checklist — Qualidade dos Testes

- [ ] Cada teste usa fixtures do `conftest.py`; sem setup duplicado inline
- [ ] Views HTMX testadas com `HTTP_HX_REQUEST: true` no header
- [ ] Nenhum teste depende de ordem de execução
- [ ] Cobertura mínima alvo: **60%** nas views listadas acima

---

## Critérios de Sucesso

| Critério | Meta |
|---|---|
| Rotas sem template correspondente | 0 |
| Views sem `select_related`/`prefetch_related` em listagens | 0 |
| Fragmentos HTMX que retornam página completa | 0 |
| Inputs sem `<label>` ou `aria-label` | 0 |
| Cobertura de testes nas 6 views críticas | >= 60% |
| Views de escrita acessíveis sem autenticação | 0 |
| Arquivo `conftest.py` com fixtures padrão | presente |

---

## Dependências Entre Fases

```
Fase 1 (explorer) → alimenta Fase 2 (frontend) e Fase 3 (backend) em paralelo
Fase 2 + Fase 3 → resultados informam Fase 4 (test-engineer) sobre o que testar
Fase 4 → executa após ter conftest.py e lista de bugs confirmada
```

## Arquivos de Referência por Agente

| Agente | Arquivos prioritários |
|---|---|
| explorer-agent | `turmas/urls.py`, `config/urls.py`, `core/urls.py`, `templates/` (tree completo) |
| frontend-specialist | `templates/base*.html`, `templates/components/`, `templates/tarefas/`, `templates/aulas/`, `templates/avaliacoes/` |
| backend-specialist | `*/views.py`, `*/models.py`, `*/forms.py`, `core/mixins.py`, `core/validators.py`, `core/adapters.py`, `atividades/github_sync.py`, `materiais/views.py` |
| test-engineer | `agents/qa.md`, `pytest.ini`, `*/tests/`, todos os `views.py` das 6 prioridades |
