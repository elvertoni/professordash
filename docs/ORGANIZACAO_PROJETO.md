# Organização do Projeto — ProfessorDash

> **Versão:** 1.0
> **Data:** Junho 2026
> **Stack:** Django 5.1 + HTMX 2.x + Alpine.js 3.x + Tailwind CSS 3.x
> **Público:** Alunos 14-18 anos, Ensino Técnico (SEED-PR)

---

## Sumário

1. [Milestones](#1-milestones)
2. [Backlog Priorizado](#2-backlog-priorizado)
3. [Release Plan](#3-release-plan)
4. [Dependências entre Tarefas](#4-dependencias-entre-tarefas)
5. [Glossário](#5-glossario)

---

## 1. Milestones

### 🚀 M0 — MVP Funcional (v1.0) ✅ Concluído

> CRUDs básicos, autenticação Google, portal do aluno funcional.

| Marco | Status | Data |
|:---|---:|---:|
| Setup do projeto (Django + Tailwind + Docker) | ✅ | 2026-04 |
| CRUD Turmas + Matrículas | ✅ | 2026-04 |
| CRUD Aulas com Markdown | ✅ | 2026-04 |
| CRUD Materiais + Upload | ✅ | 2026-04 |
| Atividades + Entregas (aluno) | ✅ | 2026-05 |
| Notas + Boletim | ✅ | 2026-05 |
| Alunos + Importação CSV | ✅ | 2026-05 |
| Dashboard do professor | ✅ | 2026-05 |
| Deploy na VPS (aulas.tonicoimbra.com) | ✅ | 2026-05 |

### ⚡ M1 — Refatoração do Formato de Aulas (v2.0-alpha)

> Consolidar documentação, habilitar modo prático, criar apostila standalone.

| Marco | Status | Sprint PRD |
|:---|---:|:---:|
| FORMATO_AULAS.md como fonte de verdade única | ✅ | S1 |
| Modo prático no renderer (aulas de código) | 🔄 Em andamento | S2 |
| Apostila standalone funcional | 🔄 Em andamento | S3 |
| Validador de markdown de aulas | ⬜ Pendente | S2.7–S2.8 |
| Testes do validador | ⬜ Pendente | S5 |

### 🎨 M2 — UX do Dashboard e Design System (v2.0-beta)

> Portar melhorias de UX da apostila para o dashboard. Refatorar CSS inline. Melhorar mobile.

| Marco | Prioridade | Esforço |
|:---|---:|---:|
| Toggle de tema persistente (S6.1) | 🔴 P0 | 🟢 Baixo |
| Anchor links em h2/h3 (S6.2) | 🔴 P0 | 🟢 Baixo |
| Copy-to-clipboard em blocos de código (S6.3) | 🔴 P0 | 🟢 Baixo |
| Modo de impressão refinado (S6.6) | 🔴 P0 | 🟢 Baixo |
| Barra de progresso no topo (S6.4) | 🟡 P1 | 🟢 Baixo |
| Sumário lateral com toggle (S6.5) | 🟡 P1 | 🟡 Médio |
| Micro-interações com HTMX/Alpine | 🟡 P1 | 🟢 Baixo |
| Acessibilidade WCAG 2.1 AA básico | 🟡 P1 | 🟡 Médio |
| Refatorar CSS inline → static/css/ | 🟡 P1 | 🔴 Alto |
| Mobile-first: responsivo para mobile | 🔴 P0 | 🟡 Médio |

### 🧊 M3 — Integração e Automatização (v2.0-rc)

> API de importação, webhooks, Hermes Agent.

| Marco | Sprint PRD |
|:---|:---:|
| API de importação de aulas (token + endpoint) | S4 |
| CLI de exportação de apostila | ✅ S3.6 |
| Script Hermes de importação | S4.5 |
| Documentação de integração (docs/api.md) | S4.3 |

### 🏁 M4 — Qualidade e Release (v2.0)

> Testes, pre-commit, snapshot tests, release final.

| Marco | Sprint PRD |
|:---|:---:|
| Testes do validador (15+ testes) | S5.1 |
| Detecção automática de modo de aula | S5.2 |
| Pre-commit hook com validação | S5.4 |
| Snapshot tests do renderer (OPC) | S5.5 |
| CHANGELOG.md + tag v2.0.0 | Pós S6 |
| Deploy produção sem regressões | Pós S6 |

---

## 2. Backlog Priorizado

### 🏆 Prioridade 0 — Fazer AGORA (Sprint 6 atual)

> Estas tarefas são as de maior impacto com menor esforço. Baseiam-se no PRD_REFATORACAO.md Sprint 6 e nas recomendações UX.

| ID | Tarefa | Esforço | Depende de | PRD Ref |
|:---|:---|---|:---:|:---:|
| **UX-01** | Toggle de tema persistente (localStorage + prefers-color-scheme) | 🟢 30min | — | S6.1 |
| **UX-02** | Anchor links em h2/h3 com slugify + clipboard | 🟢 30min | — | S6.2 |
| **UX-03** | Copy-to-clipboard em blocos `<pre><code>` | 🟢 20min | — | S6.3 |
| **UX-04** | Modo de impressão refinado (@media print) | 🟢 30min | — | S6.6 |
| **UX-05** | Barra de progresso no topo (scroll indicator) | 🟢 15min | — | S6.4 |
| **UX-06** | Auditar responsividade mobile (viewport 375px) | 🟡 1h | — | PRD §5 |
| **UX-07** | Skip-link de acessibilidade (WCAG) | 🟢 10min | — | R10 |

### ⚡ Prioridade 1 — Fazer em seguida

| ID | Tarefa | Esforço | Depende de |
|:---|:---|---|:---:|
| **UX-08** | Sumário lateral com toggle (TOC) + scroll spy | 🟡 2h | UX-02 |
| **UX-09** | Refatorar CSS de aula_detalhe.html → static/css/aula.css | 🔴 3h | — |
| **UX-10** | Refatorar JS de aula_detalhe.html → static/js/aula.js | 🟡 1h | UX-09 |
| **UX-11** | Loading states HTMX (spinner em submit, skeleton) | 🟢 1h | — |
| **UX-12** | Micro-animações fadeIn em cards (da apostila) | 🟢 30min | — |
| **UX-13** | Toast de feedback com Alpine.js (auto-dismiss) | 🟢 1h | — |
| **UX-14** | WCAG: aria-labels em botões de ícone | 🟢 30min | — |
| **UX-15** | WCAG: contraste de cores (verificar text-muted) | 🟢 20min | — |
| **UX-16** | WCAG: heading hierarchy semântica | 🟢 30min | — |
| **UX-17** | Responsivo: tabelas em mobile (stacked cards) | 🟡 1h | UX-06 |
| **UX-18** | Responsivo: navegação em telas pequenas (hamburger) | 🟡 1h | UX-06 |
| **UX-19** | S2.4 — Refatorar buildSlides() com botão Expandir | 🟡 2h | — |
| **UX-20** | S2.5 — Suporte a `## Código completo` | 🟢 1h | — |
| **UX-21** | S2.7 — Criar core/validadores.py | 🟡 2h | — |
| **UX-22** | S3.7 — Testar apostila em 3 modos de aula | 🟡 1h | — |
| **UX-23** | S3.8 — Validar modo de impressão da apostila | 🟢 30min | — |

### 🧊 Prioridade 2 — Backlog / Futuro

| ID | Tarefa | Esforço | Depende de |
|:---|:---|---|:---:|
| **UX-24** | Modo apresentação com navegação por teclado | 🟡 3h | UX-09 |
| **UX-25** | Gamificação: streak de acesso (dias consecutivos) | 🔴 4h | — |
| **UX-26** | Gamificação: badges de conquista | 🔴 4h | UX-25 |
| **UX-27** | Gamificação: barra de progresso da turma | 🟡 2h | — |
| **UX-28** | S2.6 — Syntax highlighting Prism.js (OPC) | 🟡 2h | — |
| **UX-29** | S3.9 — OG metadata (OPC) | 🟢 30min | — |
| **UX-30** | S4.2 — Autenticação por token API | 🟡 2h | — |
| **UX-31** | S4.4 — CLI importar aulas batch | 🟡 2h | — |
| **UX-32** | S4.5 — Script Hermes import | 🟢 1h | UX-31 |
| **UX-33** | S5.1 — 15 testes do validador | 🟡 2h | UX-21 |
| **UX-34** | S5.2 — Detecção automática de modo | 🟢 1h | UX-21 |
| **UX-35** | S5.3 — Modo detectado no admin Django | 🟢 30min | UX-34 |
| **UX-36** | S5.4 — Pre-commit hook | 🟡 1h | UX-21 |
| **UX-37** | S5.5 — Snapshot tests (OPC) | 🟡 2h | — |
| **UX-38** | S6.7 — Modo apresentação com teclado (OPC) | 🟡 3h | UX-24 |
| **UX-39** | WCAG: prefers-reduced-motion | 🟢 20min | — |
| **UX-40** | WCAG: aria-live para notificações dinâmicas | 🟢 30min | — |

---

## 3. Release Plan

### v2.0.0-alpha.1 (Atual — Maio 2026)
- ✅ FORMATO_AULAS.md consolidado
- ✅ Apostila standalone funcional
- ✅ Aula.gera_apostila + migration
- ✅ TOC server-side + anchors
- ✅ Export CLI criado

### v2.0.0-beta.1 (Próximo — ~Junho 2026)
- [ ] Toggle de tema persistente no dashboard
- [ ] Anchor links + copy-to-clipboard
- [ ] Barra de progresso no topo
- [ ] Modo de impressão refinado
- [ ] Responsividade mobile auditada
- [ ] Micro-interações HTMX/Alpine
- [ ] Acessibilidade WCAG básica

### v2.0.0-rc.1 (Target — Julho 2026)
- [ ] CSS refatorado para static/
- [ ] TOC lateral com toggle
- [ ] Modo apresentação com teclado
- [ ] Validador de markdown + testes
- [ ] API de importação de aulas
- [ ] Pre-commit hook

### v2.0.0 (Release — Agosto 2026)
- [ ] Todos os checkboxes não-OPC do PRD concluídos
- [ ] git tag v2.0.0
- [ ] Deploy produção sem regressões
- [ ] Hermes Agent importou 1+ aula via API
- [ ] Toni aprovou 1 apostila exportada
- [ ] CHANGELOG.md fechado

---

## 4. Dependências entre Tarefas

### Grafo de dependências (formato texto)

```
S1 (doc) ──► S2 (renderer) ──► S3 (apostila) ──► UX-09 (CSS refactor)
                                                    │
UX-01 (theme) ──► independente ◄────────────────────┘
UX-02 (anchors) ──► UX-08 (TOC) ──► UX-05 (progress)
UX-03 (copy-code) ──► independente
UX-04 (print) ──► UX-09 (ideal)
UX-06 (mobile) ──► UX-17 (tables) ──► UX-18 (nav)
UX-07 (skip-link) ──► independente
UX-10 (JS extract) ──► UX-09
UX-11 (loading) ──► independente
UX-13 (toast) ──► independente
UX-14 (aria) ──► UX-15 (contrast) ──► UX-16 (headings)
UX-21 (validator) ──► UX-33 (tests) ──► UX-34 (auto-mode) ──► UX-35 (admin mode)
UX-24 (presentation) ──► UX-09 (recomendado)
UX-25 (streak) ──► UX-26 (badges)
```

### Caminhos críticos

| Caminho | Duração estimada |
|:---|---:|
| UX-01 → UX-02 → UX-03 → UX-04 → UX-05 (P0 rápido) | **~2h** |
| UX-09 → UX-10 → UX-08 (refactor pesado) | **~5h** |
| UX-06 → UX-17 → UX-18 (mobile) | **~3h** |
| UX-21 → UX-33 → UX-34 → UX-35 (validação) | **~4h** |
| UX-25 → UX-26 (gamificação) | **~8h** |

### O que pode ser paralelizado

| Grupo | Tarefas |
|:---|---:|
| **Grupo A** (P0, sem dependências) | UX-01, UX-02, UX-03, UX-04, UX-05, UX-06, UX-07, UX-11, UX-12, UX-13 |
| **Grupo B** (Validação) | UX-21, UX-33, UX-34, UX-35 |
| **Grupo C** (Acessibilidade) | UX-14, UX-15, UX-16, UX-39, UX-40 |
| **Grupo D** (Mobile) | UX-17, UX-18, UX-06 |
| **Grupo E** (Refactor pesado) | UX-09, UX-10, UX-08 |

---

## 5. Glossário

| Termo | Significado |
|:---|---:|
| **TOC** | Table of Contents — sumário navegável |
| **TOC server-side** | TOC gerado no backend (Django + BeautifulSoup) |
| **TOC client-side** | TOC gerado no frontend (JS lendo headings do DOM) |
| **Scroll spy** | Destaque automático da seção atual no TOC conforme o scroll |
| **Anchor link** | Link para uma seção específica da página (ex.: `#introducao`) |
| **Slugify** | Função que transforma texto em URL-friendly (ex.: "Passo a Passo" → "passo-a-passo") |
| **Hero** | Seção de cabeçalho da aula/apostila (título, meta-info) |
| **Callout** | Bloco destacado (objetivo, dica, exemplo, etc.) |
| **Streak** | Dias consecutivos de acesso |
| **Badge** | Emblema visual de conquista |
| **Skip link** | Link invisível no topo da página para pular para o conteúdo principal (acessibilidade) |
| **WCAG** | Web Content Accessibility Guidelines |
| **CDN** | Content Delivery Network (Tailwind/HTMX/Alpine via CDN vs. build local) |
| **IntersectionObserver** | API JS para detectar quando um elemento entra na viewport |

---

> **Documento mantido em:** `docs/ORGANIZACAO_PROJETO.md`
> **Atualizar após cada sprint concluída.**
