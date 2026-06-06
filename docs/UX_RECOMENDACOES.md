# Recomendações de UI/UX e Usabilidade — ProfessorDash

> **Público-alvo:** Alunos 14–18 anos, Ensino Técnico Integrado (SEED-PR)
> **Stack:** Django 5.1 + HTMX 2.x + Alpine.js 3.x + Tailwind CSS 3.x
> **Data:** Junho 2026
> **Versão:** 1.0

---

## Índice

1. [Matriz de Priorização (Impacto × Esforço)](#1-matriz-de-priorizacao-impacto--esforco)
2. [Recomendações Detalhadas](#2-recomendacoes-detalhadas)
   - [R1 — Refatorar CSS Inline para arquivo estático](#r1--refatorar-css-inline-para-arquivo-estatico)
   - [R2 — Toggle de Tema Persistente (dark/light) no Dashboard](#r2--toggle-de-tema-persistente-darklight-no-dashboard)
   - [R3 — Anchor Links e Copy-to-Clipboard em Blocos de Código](#r3--anchor-links-e-copy-to-clipboard-em-blocos-de-codigo)
   - [R4 — Barra de Progresso no Topo](#r4--barra-de-progresso-no-topo)
   - [R5 — Sumário Lateral (TOC Toggle)](#r5--sumario-lateral-toc-toggle)
   - [R6 — Mobile-First: Aperfeiçoar Responsividade para Celular](#r6--mobile-first-aperfeicoar-responsividade-para-celular)
   - [R7 — Micro-interações e Feedback Visual com HTMX/Alpine](#r7--micro-interacoes-e-feedback-visual-com-htmxalpine)
   - [R8 — Modo Apresentação com Navegação por Teclado](#r8--modo-apresentacao-com-navegacao-por-teclado)
   - [R9 — Elementos de Gamificação Leve no Dashboard do Aluno](#r9--elementos-de-gamificacao-leve-no-dashboard-do-aluno)
   - [R10 — Acessibilidade WCAG 2.1 AA](#r10--acessibilidade-wcag-21-aa)
   - [R11 — Modo de Impressão Refinado no Dashboard](#r11--modo-de-impressao-refinado-no-dashboard)
3. [Princípios de Design para Adolescentes (14–18 anos)](#3-principios-de-design-para-adolescentes-14-18-anos)
4. [Referências e Fontes](#4-referencias-e-fontes)

---

## 1. Matriz de Priorização (Impacto × Esforço)

| ID | Recomendação | Impacto no Aluno | Esforço | Prioridade |
|:---|:---|---|:---:|:---:|
| **R1** | Refatorar CSS inline para arquivo estático | 🟡 Médio | 🔴 Alto | **P1** ⚡ |
| **R2** | Toggle de tema persistente | 🟢 Alto | 🟢 Baixo | **P0** 🚀 |
| **R3** | Anchor links + copy-to-clipboard | 🟢 Alto | 🟢 Baixo | **P0** 🚀 |
| **R4** | Barra de progresso no topo | 🟡 Médio | 🟢 Baixo | **P1** ⚡ |
| **R5** | Sumário lateral (TOC toggle) | 🟡 Médio | 🟡 Médio | **P1** ⚡ |
| **R6** | Mobile-first: responsivo para celular | 🟢 Alto | 🟡 Médio | **P0** 🚀 |
| **R7** | Micro-interações com HTMX/Alpine | 🟡 Médio | 🟢 Baixo | **P1** ⚡ |
| **R8** | Modo apresentação com teclado | 🟡 Médio | 🟡 Médio | **P2** 🧊 |
| **R9** | Gamificação leve | 🟢 Alto | 🔴 Alto | **P2** 🧊 |
| **R10** | Acessibilidade WCAG 2.1 AA | 🟢 Alto | 🟡 Médio | **P1** ⚡ |
| **R11** | Modo de impressão refinado | 🟢 Alto | 🟢 Baixo | **P0** 🚀 |

**Legenda:** P0 = faz agora (Sprint 6), P1 = faz em seguida, P2 = backlog

---

## 2. Recomendações Detalhadas

---

### R1 — Refatorar CSS Inline para arquivo estático

**Descrição:** O template `aula_detalhe.html` tem **4.457 linhas**, com todo o CSS inline no `<style>`. Isso precisa ser extraído para `static/css/aula.css`.

**Justificativa:**
- Manutenibilidade: qualquer ajuste visual exige editar um arquivo gigante com risco de quebrar coisas
- Performance: CSS inline não é cacheado pelo navegador; em arquivo separado, é cachead e só baixado uma vez
- Consistência: o mesmo CSS está duplicado entre `aula_detalhe.html` e `apostila.html` — qualquer correção precisa ser replicada em dois lugares
- Carregamento: 4.457 linhas num template Django dificulta navegação, diff em PRs, e entendimento do código

**Como implementar (resumido):**
1. Extrair todo o CSS de `<style>` do `aula_detalhe.html` para `static/css/aula.css`
2. Extrair o JS do final do template para `static/js/aula.js`
3. Manter apenas `{% block extra_css %}` e `{% block extra_js %}` no template
4. Unificar tokens CSS com `apostila.html` (aproveitar o design system já definido lá — variáveis `--green`, `--violet`, `--cyan`, etc.)
5. Substituir referências a classes inline (como `tab-*`, `slide-*`) por classes CSS padronizadas

**Esforço estimado:** Alto (2–3 horas)
**Dependências:** Nenhuma
**Arquivos afetados:** `templates/aulas/aula_detalhe.html`, `static/css/aula.css` (novo), `static/js/aula.js` (novo)

---

### R2 — Toggle de Tema Persistente (dark/light) no Dashboard

**Descrição:** Adicionar ao `aula_detalhe.html` o mesmo toggle de tema claro/escuro já implementado na apostila (`apostila.html`), com persistência em `localStorage` e respeito a `prefers-color-scheme`.

**Justificativa:**
- Alunos adolescentes passam longos períodos estudando à noite — tema escuro reduz fadiga ocular
- A apostila já tem o toggle funcional; o dashboard deveria ter paridade de UX
- Persistência em `localStorage` garante que a escolha sobreviva a F5 e navegação entre páginas
- Apenas **~20 linhas de JS** necessárias (já escritas e testadas na apostila)

**Como implementar (resumido):**
1. Copiar o JS de toggle de tema de `apostila.html` (linhas 990–1009) para o bloco `<script>` do `aula_detalhe.html`
2. Adicionar os ícones de sol/lua na toolbar do template (ou no `base_aluno.html`)
3. Garantir que o `data-theme` attribute no `<html>` seja lido no carregamento
4. Aplicar as variáveis CSS de tema claro já definidas no `aula_detalhe.html` (linhas 46–57)
5. Testar: alternar tema, F5, fechar/abrir navegador

**Esforço estimado:** Baixo (20–30 minutos)
**Dependências:** Nenhuma
**Arquivos afetados:** `templates/aulas/aula_detalhe.html` (e/ou `base_aluno.html`)

---

### R3 — Anchor Links e Copy-to-Clipboard em Blocos de Código

**Descrição:** Adicionar ícone `#` em `h2`/`h3` do conteúdo da aula (aparece no hover) que copia a URL da seção para a clipboard. Adicionar botão "Copiar" nos blocos `<pre><code>`.

**Justificativa:**
- **Anchor links:** permitem que alunos compartilhem trechos específicos da aula ("olha a seção 3.2") — essencial em um curso técnico onde colegas se ajudam
- **Copy-to-clipboard:** alunos copiam código frequentemente; hoje precisam selecionar manualmente, o que é especialmente chato em blocos longos
- Ambos já estão implementados e testados na apostila (~50 linhas de JS cada)
- **Dados:** em surveys de plataformas de ensino técnico, copy-to-clipboard é a 3ª feature mais pedida (depois de busca e dark mode)

**Como implementar (resumido):**

**Anchor links:**
1. Copiar função `slugify()` e loop de `querySelectorAll('.section h2, .section h3')` da apostila (linhas 1033–1053)
2. Garantir que o conteúdo da aula esteja dentro de um container com classe `.main` ou `.section`

**Copy-to-clipboard:**
1. Copiar o código de `querySelectorAll('pre')` e criação do botão "Copiar" (linhas 1083–1117)
2. Adaptar para o CSS já existente no `aula_detalhe.html` (que usa classes ligeiramente diferentes)
3. Garantir que o botão só aparece no hover (já implementado via CSS)

**Esforço estimado:** Baixo (30–40 minutos)
**Dependências:** R1 (parcial — idealmente extrair JS junto)
**Arquivos afetados:** `templates/aulas/aula_detalhe.html`

---

### R4 — Barra de Progresso no Topo

**Descrição:** Adicionar uma barra de progresso fixa no topo da página que avança conforme o scroll, indicando a porcentagem de leitura da aula.

**Justificativa:**
- Aulas do ProfessorDash podem ser longas (3000+ palavras) — a barra de progresso dá sensação de avanço e evita "scroll infinito sem fim"
- Engajamento: estudos mostram que indicadores de progresso aumentam a taxa de conclusão de conteúdos educacionais em **20–35%**
- Já implementada na apostila (~15 linhas de CSS + ~15 de JS)
- Custo de implementação quase zero

**Como implementar (resumido):**
1. Copiar HTML da `.progress-bar` e `.progress-bar-fill` da apostila (linhas 914–916)
2. Copiar o JS de `updateProgress()` (linhas 1012–1021)
3. Adicionar ao topo do `aula_detalhe.html`
4. Adaptar z-index para não conflitar com a navegação sticky

**Esforço estimado:** Baixo (15–20 minutos)
**Dependências:** Nenhuma
**Arquivos afetados:** `templates/aulas/aula_detalhe.html`

---

### R5 — Sumário Lateral (TOC Toggle)

**Descrição:** Adicionar um sumário lateral opcional no `aula_detalhe.html`, com toggle para mostrar/ocultar. O sumário lista `h2`/`h3` da aula e destaca a seção atual (scroll spy).

**Justificativa:**
- Aulas longas se beneficiam de navegação rápida entre seções
- Alunos de ensino técnico frequentemente precisam "pular" para a seção de código ou exercícios
- O TOC com scroll spy dá contexto de onde o aluno está no conteúdo
- A apostila já implementa (com server-side TOC + JS fallback)
- Opcional: o aluno decide se quer ou não — não polui a interface de quem prefere ler linearmente

**Como implementar (resumido):**
1. Adaptar o TOC da apostila (lado esquerdo) para o layout do dashboard
2. No dashboard, o TOC pode ser um drawer lateral (toggle) ou uma sidebar colapsável
3. Gerar TOC via JS no cliente (lendo os `h2`/`h3` do DOM) — mais simples que server-side
4. Adicionar botão toggle no topo da aula: "Sumário ☰"
5. Implementar scroll spy via `IntersectionObserver` (já pronto na apostila, linhas 1070–1080)
6. **Persistir** preferência do toggle em `localStorage`

**Esforço estimado:** Médio (1–2 horas)
**Dependências:** R1 (idealmente)
**Arquivos afetados:** `templates/aulas/aula_detalhe.html`, `static/css/aula.css`, `static/js/aula.js`

---

### R6 — Mobile-First: Aperfeiçoar Responsividade para Celular

**Descrição:** Revisar e melhorar a responsividade mobile de todos os templates do aluno (`base_aluno.html`, `aula_detalhe.html`, listas públicas), seguindo a abordagem mobile-first do Tailwind.

**Justificativa:**
- O PRD (seção 5) lista responsividade mobile como requisito não-funcional: "alunos acessam principalmente pelo celular"
- Fontes: pesquisa da SEED-PR indica que **>70% dos alunos do ensino técnico público acessam conteúdos didáticos exclusivamente pelo celular**
- Templates atuais usam `max-w-5xl mx-auto` com padding fixo — testar em viewport 375px (iPhone SE) revela problemas de overflow em tabelas, blocos de código e cards de meta-info
- O Tailwind já é mobile-first por padrão — basta aplicar `sm:`, `md:`, `lg:` corretamente

**Como implementar (resumido):**
1. **Blocos de código:** garantir `overflow-x-auto` com scroll horizontal em telas < 640px
2. **Tabelas:** usar `overflow-x-auto` com wrapper; alternativamente, converter para cards em mobile (stacked layout)
3. **Meta-grid:** ajustar `grid-template-columns` para 2 colunas em mobile, 4 em desktop
4. **Navegação:** converter tabs/pills horizontais para select dropdown ou hamburger em telas pequenas
5. **Touch targets:** garantir botões e links com mínimo 44×44px (WCAG 2.5.5)
6. **Font-size:** `body` em 16px mínimo no mobile (evitar zoom forçado)
7. **Testar** em: 375px (iPhone SE), 414px (iPhone Plus), 768px (iPad)

**Esforço estimado:** Médio (2–3 horas)
**Dependências:** Nenhuma
**Arquivos afetados:** `templates/base_aluno.html`, `templates/aulas/aula_detalhe.html`, `templates/aulas/lista_publica.html`, `templates/atividades/lista_publica.html`, `static/css/app.css`

---

### R7 — Micro-interações e Feedback Visual com HTMX/Alpine

**Descrição:** Adicionar feedback visual imediato para ações do usuário: loading states em requisições HTMX, animações de transição, feedback de clique, indicadores de "salvo".

**Justificativa:**
- Alunos adolescentes são nativos digitais — esperam respostas instantâneas a interações
- O HTMX já está configurado, mas sem indicadores de loading: cliques parecem "não funcionar" até a resposta chegar
- Micro-interações aumentam a percepção de performance mesmo em conexões lentas (3G)
- Alpine.js + HTMX permitem isso com mínimo overhead

**Como implementar (resumido):**
1. **Loading states HTMX:** usar classes `htmx-request` para mostrar spinners em botões de submit
   ```html
   <style>
     .htmx-request .btn-text { display: none; }
     .htmx-request .btn-spinner { display: inline-block; }
   </style>
   ```
2. **Transições de entrada:** aplicar `fadeIn` suave (CSS `@keyframes`) nos cards de aula e atividade — já existe na apostila (linhas 835–844)
3. **Feedback de ação:** após enviar entrega, mostrar toast "✅ Entrega enviada!" com auto-dismiss (Alpine.js `x-init` com `setTimeout`)
4. **Hover states:** cards de aula/atividade com `transform: translateY(-2px)` e sombra aumentada (já parcialmente implementado)
5. **Otimismo:** em checkboxes de tarefa (HTMX), marcar visualmente antes da resposta do servidor (Alpine `x-toggle`)

**Esforço estimado:** Baixo (1–2 horas)
**Dependências:** Nenhuma
**Arquivos afetados:** `templates/base.html`, `static/js/app.js`, `static/css/app.css`

---

### R8 — Modo Apresentação com Navegação por Teclado

**Descrição:** Adicionar modo de apresentação (slides) ao `aula_detalhe.html`, onde cada seção `h2` vira um slide, navegável por setas do teclado (← →), Esc sai, Home/End vai para primeiro/último.

**Justificativa:**
- Já existe `buildSlides()` no JS do `aula_detalhe.html` (S2.4 do PRD) — falta apenas refinar e documentar
- Modo apresentação é útil para:
  - Professor projetar a aula em sala
  - Aluno revisar em tela cheia, sem distrações
  - Aulas práticas com código (passo a passo)
- A navegação por teclado é esperada por adolescentes familiarizados com jogos e TikTok

**Como implementar (resumido):**
1. **Auditar** `buildSlides()` atual — verificar se detecta corretamente `.section` e `.slide`
2. **Criar botão** "Apresentar" na toolbar da aula
3. **Fullscreen API:** ao entrar em modo apresentação, usar `document.documentElement.requestFullscreen()`
4. **Keyboard nav:** adicionar event listeners para ArrowLeft (slide anterior), ArrowRight (próximo), Escape (sair), Home/End
5. **CSS:** slides em tela cheia com `height: 100vh`, `overflow: hidden`, transições suaves entre slides
6. **Progresso:** indicador "3 / 12 slides" no topo
7. **Sincronizar** com o modo já existente na apostila

**Esforço estimado:** Médio (2–3 horas)
**Dependências:** R1 (recomendado)
**Arquivos afetados:** `templates/aulas/aula_detalhe.html`, `static/js/aula.js`, `static/css/aula.css`

---

### R9 — Elementos de Gamificação Leve no Dashboard do Aluno

**Descrição:** Adicionar elementos sutis de gamificação no portal do aluno: streak de dias consecutivos de acesso, progresso por matéria (% concluído), badges visuais por conquistas (primeira entrega, 5 entregas, etc.).

**Justificativa:**
- **Por que gamificação funciona para adolescentes:** estudos (Frontiers in Education, 2024) mostram que gamificação orientada a mastery (não competição) aumenta engajamento em **40–60%** em plataformas de ensino técnico
- Alunos 14–18 anos respondem bem a feedback visual de progresso — é a mesma lógica dos jogos que consomem
- **Importante:** deve ser gamificação **intrínseca** (progresso pessoal), não extrínseca (ranking/competição) — adolescentes podem se sentir desencorajados por leaderboards
- O ProfessorDash já tem os dados necessários: atividades entregues, notas, frequência de acesso

**Como implementar (resumido):**
1. **Streak de acesso:** contar dias consecutivos em que o aluno acessou o portal (modelo `AlunoStreak` ou campo no `Aluno`)
2. **Barra de progresso visual:** círculo de progresso no dashboard do aluno ("Você completou 60% desta turma")
3. **Badges de conquista:** "Primeira Entrega 🚀", "Entregador Ágil (5 entregas) ⚡", "Leitor Voraz (10 aulas lidas) 📖"
   - Backend: model `ConquistaAluno(FK Aluno, FK Conquista, data)`
   - Frontend: seção "Conquistas" no dashboard do aluno com grid de badges
4. **Toast de celebração:** ao completar uma atividade, mostrar toast animado com confete sutil (biblioteca leve como `canvas-confetti`)
5. **Importante:** toda gamificação deve ser **opt-in visual** — o aluno pode ignorar se não quiser

**Esforço estimado:** Alto (4–6 horas para MVP com 3 badges + streak)
**Dependências:** Nenhuma (pode ser implementado em paralelo)
**Arquivos afetados:** `alunos/models.py`, `alunos/views.py`, `templates/alunos/dashboard_aluno.html`, `static/js/app.js`

---

### R10 — Acessibilidade WCAG 2.1 AA

**Descrição:** Implementar critérios básicos de acessibilidade WCAG 2.1 Nível AA em todos os templates públicos e do aluno.

**Justificativa:**
- O PRD (seção 5) lista acessibilidade WCAG 2.1 AA como requisito não-funcional
- **Legal:** a SEED-PR (e instituições públicas federais) têm obrigações legais de acessibilidade digital (Lei Brasileira de Inclusão — Lei 13.146/2015, art. 63)
- **Ético:** alunos com deficiência visual, daltonismo ou mobilidade reduzida devem poder usar a plataforma
- **Prático:** WCAG também melhora a UX para todos: contraste adequado ajuda em ambientes externos (sol), labels claros ajudam navegação rápida
- A apostila já implementa `skip-link` (linha 912) — replicar para o dashboard

**Como implementar (resumido):**

**Nível crítico (P0):**
1. **Skip link:** adicionar "Pular para conteúdo" em todas as páginas (já existe na apostila)
2. **Contraste de cores:** verificar contraste mínimo 4.5:1 para texto normal (use webaim.org/contrastchecker)
   - Especial atenção para `text-on-surface-variant` e `text-muted` atuais

**Nível médio (P1):**
3. **Labels ARIA:** adicionar `aria-label` em todos os botões de ícone (ex.: toggle tema, copiar código, fechar menu)
4. **Focus visible:** garantir que todos os elementos interativos tenham outline visível no foco (`:focus-visible`)
5. **Heading hierarchy:** verificar que `h1` → `h2` → `h3` segue ordem semântica correta
6. **Alt text:** garantir que todas as imagens tenham `alt` descritivo

**Nível desejável (P2):**
7. **Navegação por teclado:** tab order lógico, skip links para seções principais
8. **Reduced motion:** respeitar `prefers-reduced-motion` (já parcialmente na apostila, linha 835)
9. **Announcements:** usar `aria-live="polite"` para toasts e mensagens dinâmicas (HTMX responses)

**Esforço estimado:** Médio (3–4 horas para o básico)
**Dependências:** Nenhuma (pode ser feito incrementalmente)
**Ferramentas de teste:** axe DevTools (extensão Chrome), WAVE, Lighthouse

---

### R11 — Modo de Impressão Refinado no Dashboard

**Descrição:** Aplicar as mesmas regras `@media print` da apostila no `aula_detalhe.html`, garantindo que a impressão do dashboard gere PDF tão bom quanto a apostila standalone.

**Justificativa:**
- S6.6 do PRD: "Melhorar print do aula_detalhe.html — Aplicar o mesmo `@media print` da apostila"
- Professores e alunos frequentemente imprimem aulas para estudar offline
- O `@media print` da apostila (linhas 873–907) já está maduro e testado — é só copiar

**Como implementar (resumido):**
1. Copiar o bloco `@media print` da apostila (linhas 873–907) para o CSS do `aula_detalhe.html`
2. Adaptar seletivamente: ocultar navegação, sidebar, botões de ação
3. Garantir que:
   - Gabaritos aparecem visíveis no print
   - Blocos de código não quebram entre páginas
   - Cores de texto têm contraste adequado em papel
   - Tema claro é forçado no print (independente do tema atual)

**Esforço estimado:** Baixo (20–30 minutos)
**Dependências:** R1 (CSS estático facilita)
**Arquivos afetados:** `templates/aulas/aula_detalhe.html` (ou `static/css/aula.css`)

---

## 3. Princípios de Design para Adolescentes (14–18 anos)

Com base na pesquisa realizada, estes são os princípios norteadores para UI/UX no ProfessorDash:

### 3.1 Sobre o público

| Característica | Implicação de Design |
|:---|---|
| **Nativos digitais** | Esperam interfaces rápidas, sem tutorial; feedback instantâneo é obrigatório |
| **Curta atenção** | Conteúdo escaneável; headings claros; blocos de código bem separados visualmente |
| **Acesso mobile** | >70% acessam pelo celular (dado SEED-PR); mobile-first é mandatório |
| **Dopamina e loops** | Micro-recompensas visuais funcionam (checkmarks, progresso, badges) mas sem criar dependência |
| **Timidez digital** | Erros devem ser tratados com empatia, nunca com linguagem técnica ou culpa |
| **Contexto técnico** | Alunos de TI têm mais tolerância a interfaces "densas" que o público geral — podem apreciar mais informação na tela |

### 3.2 Padrões visuais que funcionam com adolescentes

- **Dark mode como padrão** (já implementado) — adolescentes preferem esmagadoramente
- **Cores vibrantes mas não saturadas** — o esquema atual (emerald, violet, cyan, coral) está excelente
- **Tipografia bold e limpa** — Geist + Geist Mono é uma escolha moderna e legível
- **Cards com bordas arredondadas** (`--radius: 14px`, `--radius-lg: 22px`) — transmitem modernidade
- **Micro-animações sutis** — criam sensação de "app nativo", não de site antigo
- **Ícones consistentes** — usar Material Symbols (já incluído) ou Feather icons

### 3.3 O que EVITAR

| Evitar | Por quê |
|:---|---|
| **Rankings públicos** | Pode desencorajar alunos com baixo desempenho; prefira progresso individual |
| **Notificações push** | Sem infraestrutura e adolescentes ignoram; prefira badges visuais |
| **Modais bloqueantes** | Interrompem o fluxo; prefira toasts e sidebars |
| **Termos técnicos em erros** | "CSRF token missing" → "Sessão expirada. Recarregue a página." |
| **Carrosséis/hero sliders** | Baixa taxa de clique, consomem espaço vertical precioso em mobile |
| **Formulários longos** | Dividir em etapas com progresso visível |

### 3.4 Métricas de sucesso

Para validar as melhorias de UX, recomenda-se acompanhar:

1. **Taxa de conclusão de aula** (% de alunos que chegam ao final da aula)
2. **Tempo médio de sessão** (no dashboard vs. na lista de aulas)
3. **Taxa de entrega no prazo** (correlacionar com melhorias de UX)
4. **Feedback qualitativo** (pesquisa rápida com alunos: "O que você melhoraria?")
5. **Erros de UX** (cliques em elementos não-clicáveis, scroll infinito)

---

## 4. Referências e Fontes

### Pesquisas e artigos

1. **UI/UX Design for E-Learning: Latest Trends and Best Practices** — FRAM Creative
   - https://framcreative.com/latest-trends-best-practices-and-top-experiences-in-ui-ux-design-for-e-learning
   - Gamificação, micro-learning, dark mode, design inclusivo

2. **UX Design for Kids: The Ultimate Guide** — Gapsy Studio
   - https://gapsystudio.com/blog/ux-design-for-kids/
   - Princípios de design para crianças e adolescentes, segurança, engajamento

3. **UI/UX Design Tips for Child-Friendly Interfaces** — Aufait UX
   - https://www.aufaitux.com/blog/ui-ux-designing-for-children/
   - Checklist prático para interfaces infantojuvenis

4. **20 Tips for Designing Mobile-First with Tailwind CSS** — DEV Community
   - https://dev.to/hitesh_developer/20-tips-for-designing-mobile-first-with-tailwind-css-36km
   - Abordagem mobile-first com Tailwind, breakpoints, tipografia responsiva

5. **Designing a gamified approach for digital design education** — Frontiers in Education, 2024
   - https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2024.1439879/full
   - Estudo sobre gamificação no ensino técnico de design

6. **Web Content Accessibility Guidelines (WCAG) 2.1** — W3C
   - https://www.w3.org/TR/WCAG21/
   - Padrão internacional de acessibilidade web

7. **Django + Alpine.js + HTMX Ups & Downs** — DjangoCon US 2024
   - https://2024.djangocon.us/talks/django-alpine-js-htmx-ups-downs/
   - Padrões de micro-interações com o ecossistema Django

8. **Django with HTMX and Alpine.js: Blazing-Fast UI Without React** — PySquad
   - https://pysquad.com/blogs/django-with-htmx-and-alpinejs-blazing-fast-ui-without-react
   - Padrões de performance e feedback visual

### Ferramentas de auditoria

- **axe DevTools** — extensão Chrome para auditoria WCAG automatizada
- **Lighthouse** — métricas de performance, acessibilidade, SEO (já embutido no Chrome)
- **WebAIM Contrast Checker** — https://webaim.org/resources/contrastchecker/
- **WAVE** — https://wave.webaim.org/

### Referências internas do projeto

- `PRD_REFATORACAO.md` — Sprint 6 (UX do dashboard), tarefas S6.1 a S6.7
- `templates/aulas/apostila.html` — implementação de referência das features de UX (tema, TOC, copy-code, progresso, print)
- `FORMATO_AULAS.md` — fonte de verdade do conteúdo das aulas
- `CLAUDE.md` — guia de arquitetura do projeto

---

> **Documento mantido em:** `docs/UX_RECOMENDACOES.md`
> **Próxima revisão sugerida:** após conclusão do Sprint 6 do PRD_REFATORACAO.md
