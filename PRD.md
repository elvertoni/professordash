# PRD — ProfessorDash
**Sistema de Gerenciamento de Turmas e Materiais Didáticos**
**Professor Toni Coimbra · SEED-PR · Curso Técnico em Desenvolvimento de Sistemas**

---

## 1. Visão Geral

### 1.1 Problema
O professor Toni gerencia mais de 10 turmas ativas com alunos, aulas, atividades e entregas atualmente distribuídos no Notion. Embora funcional, o Notion apresenta limitações para o caso de uso docente: ausência de fluxos específicos para envio de entregas por alunos, controle de notas, acesso público por turma e integração com ferramentas de desenvolvimento (arquivos ZIP, código, markdown).

### 1.2 Solução
**ProfessorDash** — uma aplicação web própria, hospedada na VPS do professor, que centraliza 100% da gestão pedagógica em uma interface pensada especificamente para o contexto do curso técnico de TI. Substitui o Notion completamente.

### 1.3 Objetivo Principal
Prover ao professor um painel administrativo completo e aos alunos um portal de acesso a materiais e envio de atividades — tudo sob o domínio `tonicoimbra.com`.

---

## 2. Personas

### Persona 1 — Professor (Admin)
- **Quem**: Toni Coimbra, único usuário admin
- **Objetivos**: Criar/gerenciar turmas, cadastrar aulas, publicar materiais, lançar atividades, visualizar e avaliar entregas, registrar notas
- **Acesso**: Login exclusivo (credenciais próprias + 2FA opcional)

### Persona 2 — Aluno
- **Quem**: Estudantes do curso técnico, ~30 por turma, 10+ turmas
- **Objetivos**: Visualizar materiais da sua turma, baixar arquivos, acessar links, enviar atividades
- **Acesso**: Login com Google **ou** link público da turma (sem cadastro)

---

## 3. Stack Recomendada

| Camada | Tecnologia | Justificativa |
|---|---|---|
| Backend | **Django 5.x** | Já utilizado no TRIARIO; ORM robusto, admin nativo, file handling, auth built-in |
| Frontend | **HTMX + Alpine.js** | Server-rendered, sem build step, interatividade suficiente para o caso de uso |
| CSS | **Tailwind CSS** | Utilitário, produtivo, ótimo resultado visual com pouco código |
| Auth | **django-allauth** | Google OAuth2 + sessão local para o admin |
| Storage | **VPS local + Django FileField** | Simples para começar; pode migrar para S3/R2 depois |
| Deploy | **Docker + Caddy** | Já configurado na VPS; HTTPS automático via Caddy |
| DB | **PostgreSQL** | Confiável, já disponível na VPS |

> **Nota**: A escolha HTMX + Alpine elimina a necessidade de um frontend separado (React/Vue/Next.js), reduzindo significativamente a complexidade de deploy e manutenção para um projeto pessoal. Evolução para REST API + SPA é possível no futuro.

---

## 4. Funcionalidades

### 4.1 Módulo: Turmas

**Admin (Professor)**
- [ ] Criar turma (nome, código, período, ano letivo, descrição)
- [ ] Editar / arquivar turma
- [ ] Gerar link público por turma (token único, revogável)
- [ ] Listar alunos por turma
- [ ] Importar lista de alunos via CSV
- [ ] Visualizar painel resumo da turma (aulas, atividades pendentes, entregas)

**Aluno**
- [ ] Acessar turma via link público (sem login) ou Google Login
- [ ] Ver informações da turma (nome, professor, período)

---

### 4.2 Módulo: Aulas / Plano de Ensino

**Admin**
- [ ] Criar aula (título, data, número da aula, conteúdo descritivo em Markdown)
- [ ] Reordenar aulas via drag-and-drop
- [ ] Marcar aula como "realizada"
- [ ] Duplicar aula para outra turma
- [ ] Visualização de calendário do plano de ensino

**Aluno**
- [ ] Visualizar lista de aulas da turma
- [ ] Ver conteúdo detalhado de cada aula (Markdown renderizado)

---

### 4.3 Módulo: Materiais Didáticos

**Admin**
- [ ] Upload de arquivo (PDF, ZIP, código-fonte)
- [ ] Inserir material em formato HTML/Markdown (renderizado inline)
- [ ] Adicionar links externos (YouTube, GitHub, sites)
- [ ] Associar material a uma aula ou à turma de forma geral
- [ ] Definir visibilidade: público (sem login) ou restrito (Google Login)
- [ ] Editar / excluir material

**Aluno**
- [ ] Visualizar e baixar materiais associados à turma/aula
- [ ] Visualizar conteúdo HTML/Markdown diretamente no portal
- [ ] Acessar links externos

**Tipos de arquivo suportados**
- PDF / slides (.pdf, .pptx)
- Arquivos compactados (.zip, .rar)
- Código-fonte (.py, .js, .html, .css, .sql, etc.)
- Documentos (.docx, .txt)
- Conteúdo inline (Markdown + HTML renderizado)

---

### 4.4 Módulo: Atividades

**Admin**
- [ ] Criar atividade (título, descrição em Markdown, data de entrega, valor em pontos)
- [ ] Associar atividade a uma aula ou turma
- [ ] Definir tipo: entrega de arquivo, texto, link (GitHub/replit), ou múltipla escolha
- [ ] Visualizar dashboard de entregas (quem entregou / quem não entregou)
- [ ] Baixar todas as entregas de uma atividade em ZIP
- [ ] Reabrir prazo para aluno específico

**Aluno**
- [ ] Visualizar atividades da turma (abertas, encerradas, entregues)
- [ ] Enviar entrega (arquivo, texto ou link)
- [ ] Reenviar entrega até o prazo (se habilitado)
- [ ] Ver status: "Entregue", "Pendente", "Em atraso"

---

### 4.5 Módulo: Notas / Avaliações

**Admin**
- [ ] Lançar nota por entrega (0–10 ou pontos customizados)
- [ ] Adicionar feedback textual por entrega
- [ ] Visualizar boletim da turma (grid aluno × atividade)
- [ ] Calcular média por aluno automaticamente
- [ ] Exportar boletim em CSV / PDF
- [ ] Definir pesos por atividade (opcional)

**Aluno**
- [ ] Ver suas próprias notas e feedback do professor
- [ ] Ver média parcial (se habilitado pelo professor)

---

### 4.6 Módulo: Alunos

**Admin**
- [ ] Cadastrar aluno manualmente (nome, e-mail, matrícula)
- [ ] Importar alunos via CSV
- [ ] Vincular conta Google ao cadastro do aluno
- [ ] Visualizar perfil do aluno (entregas, notas, frequência de acesso)
- [ ] Mover aluno entre turmas

**Aluno**
- [ ] Vincular conta Google para login personalizado
- [ ] Visualizar próprio perfil (turma, atividades, notas)

---

### 4.7 Módulo: Dashboard do Professor

- [ ] Visão geral: turmas ativas, total de alunos, atividades abertas
- [ ] Feed de entregas recentes (últimas 24h)
- [ ] Alertas: atividades próximas do prazo, entregas não avaliadas
- [ ] Acesso rápido às turmas mais recentes
- [ ] Estatísticas: taxa de entrega por atividade, média da turma

---

## 5. Requisitos Não-Funcionais

| Requisito | Detalhe |
|---|---|
| **Hospedagem** | VPS Contabo, Ubuntu 24.04 LTS |
| **Domínio** | Subdomínio sugerido: `aulas.tonicoimbra.com` ou `prof.tonicoimbra.com` |
| **HTTPS** | Automático via Caddy |
| **Deploy** | Docker Compose (app + postgres + caddy) |
| **Backup** | Dump PostgreSQL diário via cron + backup de arquivos uploaded |
| **Performance** | Suporte a 300+ alunos simultâneos sem degradação |
| **Responsividade** | Mobile-first (alunos acessam principalmente pelo celular) |
| **Segurança** | CSRF, autenticação por sessão, rate limiting em uploads |
| **Acessibilidade** | WCAG 2.1 AA básico |

---

## 6. Modelo de Acesso e Autenticação

```
┌─────────────────────────────────────────────────────────┐
│                   aulas.tonicoimbra.com                 │
├─────────────────┬───────────────────────────────────────┤
│   /admin/*      │   /turma/<token-publico>/*            │
│   Login próprio │   Acesso público (sem login)          │
│   (Professor)   │   - Materiais públicos                │
│                 │   - Ver aulas                         │
│   /painel/*     ├───────────────────────────────────────┤
│   Dashboard     │   /turma/<token>/entrar (Google Login)│
│   completo      │   Acesso autenticado (Aluno)          │
│                 │   - Enviar entregas                   │
│                 │   - Ver notas e feedback              │
└─────────────────┴───────────────────────────────────────┘
```

**Regras:**
- Material pode ser marcado como "público" (link da turma basta) ou "restrito" (requer Google Login)
- Entregas sempre requerem Google Login (para identificar o aluno)
- Notas e feedback sempre requerem Google Login
- O professor acessa via `/admin/` com senha própria (não Google)

---

## 7. Modelo de Dados (Entidades Principais)

```
Turma
  ├── id, nome, codigo, periodo, ano_letivo, token_publico
  ├── → Alunos (M2M via Matricula)
  ├── → Aulas
  └── → Atividades

Aula
  ├── id, turma, titulo, numero, data, conteudo_md, realizada
  └── → Materiais

Material
  ├── id, aula/turma, titulo, tipo (pdf|zip|codigo|markdown|link)
  ├── arquivo (FileField) | url | conteudo_html
  └── visibilidade (publico|restrito)

Atividade
  ├── id, turma, aula, titulo, descricao_md, prazo, valor_pontos
  ├── tipo (arquivo|texto|link|quiz)
  └── → Entregas

Entrega
  ├── id, atividade, aluno, data_envio, arquivo/texto/url
  ├── nota, feedback, data_avaliacao
  └── status (pendente|entregue|atrasado|avaliado)

Aluno
  ├── id, nome, email, matricula, google_id
  └── → Matriculas (turmas)

Matricula
  └── aluno, turma, data_matricula, ativa
```

---

## 8. Sprints Sugeridas

### Sprint 0 — Setup (3–5 dias)
- [ ] Estrutura Django + HTMX + Tailwind
- [ ] Docker Compose (app + postgres)
- [ ] Caddy config no subdomínio
- [ ] django-allauth (Google OAuth)
- [ ] Deploy inicial na VPS

### Sprint 1 — Core Admin (5–7 dias)
- [ ] CRUD de Turmas
- [ ] CRUD de Aulas (com Markdown)
- [ ] CRUD de Materiais (upload de arquivos)
- [ ] Link público por turma funcional
- [ ] Portal do aluno (visualização básica)

### Sprint 2 — Atividades e Entregas (5–7 dias)
- [ ] CRUD de Atividades
- [ ] Fluxo de entrega (aluno envia arquivo/texto/link)
- [ ] Dashboard de entregas por atividade
- [ ] Download em ZIP das entregas

### Sprint 3 — Notas e Boletim (3–5 dias)
- [ ] Lançamento de notas por entrega
- [ ] Feedback textual
- [ ] Boletim da turma (grid)
- [ ] Exportação CSV/PDF
- [ ] Visualização do aluno (suas notas)

### Sprint 4 — Dashboard e Polimento (3–5 dias)
- [ ] Dashboard do professor com KPIs
- [ ] Alertas de prazo e entregas pendentes
- [ ] Importação de alunos via CSV
- [ ] Mobile responsiveness
- [ ] Testes e refinamentos

---

## 9. Fora do Escopo (v1)

- Videoaulas hospedadas na plataforma (usar YouTube + link externo)
- Chat professor ↔ aluno (pode ser integrado via n8n/WhatsApp futuramente)
- Fórum / comentários por aula
- Gamificação / ranking
- App mobile nativo
- Integração com SIGA/sistemas da SEED-PR
- Múltiplos professores / multi-tenant

---

## 10. Integrações Futuras (Roadmap v2)

| Integração | Descrição |
|---|---|
| **n8n** | Notificações WhatsApp para alunos (nova atividade, prazo, nota) |
| **Google Drive** | Armazenamento alternativo para materiais |
| **IA (Claude API)** | Correção automática assistida de entregas |
| **Telegram Bot** | Notificações para o professor via OpenClaw |
| **API REST** | Exposição de endpoints para integração com outros sistemas |

---

## 11. Critérios de Aceite (MVP)

- [ ] Professor consegue criar turma e gerar link público em menos de 2 minutos
- [ ] Aluno acessa materiais via link público sem precisar criar conta
- [ ] Aluno com Google Login consegue enviar entrega em menos de 3 cliques
- [ ] Professor visualiza todas as entregas de uma atividade e baixa em ZIP
- [ ] Boletim da turma é exportável em CSV
- [ ] Sistema funciona 100% no celular (responsivo)
- [ ] Deploy estável na VPS com HTTPS

---

*Versão 1.0 — Março 2026*
*Autor: Toni Coimbra*
