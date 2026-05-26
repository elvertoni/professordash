# PLAN_REFATORACAO.md — Plano de Execução da Refatoração v2.0

Este documento descreve o plano detalhado de orquestração para executar as tarefas pendentes do `PRD_REFATORACAO.md`.

---

## 👥 Orquestração de Agentes

Para atender ao requisito de orquestração, dividiremos o trabalho entre **4 agentes especializados**:

| Agente | Domínio | Responsabilidade nesta Refatoração |
|---|---|---|
| `project-planner` | Planejamento | Estruturação de planos, coordenação e controle de entregas. |
| `backend-specialist` | Django & Lógica | Implementação do validador de Markdown, autenticação via API Token, comandos de gerenciamento Django e modelo `ApiToken`. |
| `frontend-specialist` | UI/UX (CSS/JS) | JS para expansão/colapso de código longo, blocos de Prism.js, temas persistentes, anchor links, barra de progresso e estilo de impressão. |
| `test-engineer` | Qualidade & Testes | Escrita de testes unitários (`pytest`), validação de impressão PDF e verificação manual nos múltiplos navegadores. |
| `devops-engineer` | Scripts & Integração | Script wrapper para o Hermes (`hermes_importar.sh`) e configuração de ganchos Git (`pre-commit`). |

---

## 📅 Sprints e Tarefas a Executar

### 🛠️ Sprint 2 (Pendentes) — Modo Prático no Renderer

#### 👨‍💻 Responsabilidade: `frontend-specialist` (S2.4, S2.5, S2.6) e `backend-specialist` (S2.7, S2.8)

*   **[S2.4] Refatoração do JS em `aula_detalhe.html`**:
    *   Habilitar comportamento dinâmico para colapsar blocos `pre` com mais de 30 linhas (com botões de "Expandir" e "Recolher").
    *   Adicionar as classes e estilos correspondentes no cabeçalho CSS do template.
*   **[S2.5] Suporte a `## Código completo`**:
    *   Detectar se a seção H2 é `Código completo` e aplicar uma estilização especial (`.section-codigo` com fundo escuro e sem margens internas).
*   **[S2.6] Prism.js Syntax Highlighting**:
    *   Integrar Prism.js de forma eficiente, importando arquivos CSS/JS estáticos locais para evitar chamadas de CDN externas lentas.
*   **[S2.7] Validador de Markdown (`core/validadores.py`)**:
    *   Escrever `validar_markdown_aula(texto: str) -> list[str]` para checar conformidade com `FORMATO_AULAS.md`.
*   **[S2.8] Integração no Model `Aula.clean()`**:
    *   Garantir que a validação dispare ValidationError impedindo o salvamento de conteúdo inválido em modo professor.

---

### 📄 Sprint 3 (Pendentes) — Testes da Apostila Standalone

#### 👨‍🔬 Responsabilidade: `test-engineer` (S3.7, S3.8) e `frontend-specialist` (S3.9)

*   **[S3.7] Testes de Paridade**:
    *   Validar visualmente as apostilas renderizadas nos três modos definidos: conceitual, prático (com blocos de código grandes) e aulas longas.
*   **[S3.8] Validação de Impressão (PDF)**:
    *   Verificar estilos `@media print` para assegurar que sumários, botões de ação e headers sejam ocultados corretamente no PDF gerado.
*   **[S3.9] OpenGraph Metadata**:
    *   Adicionar tags `<meta>` de SEO e preview em `templates/aulas/apostila.html`.

---

### 🔌 Sprint 4 (Pendentes) — Importação e Integração Hermes

#### 👨‍💻 Responsabilidade: `backend-specialist` (S4.1-S4.4) e `devops-engineer` (S4.5)

*   **[S4.1] Auditoria de `AulaImportarMdView`**:
    *   Garantir que a importação existente em `aulas/views.py` chame a nova função `validar_markdown_aula`.
*   **[S4.2] Autenticação por Token (Model `ApiToken`)**:
    *   Criar o modelo `ApiToken` associado a `User`.
    *   Implementar autenticação via header HTTP `Authorization: Token <chave>` na view de importação.
*   **[S4.3] Documentação da API**:
    *   Criar `docs/api.md` com exemplos práticos utilizando `curl` e `Python`.
*   **[S4.4] CLI de Importação**:
    *   Criar o comando de gerenciamento `python manage.py importar_aulas` para processamento batch local.
*   **[S4.5] Script Wrapper `hermes_importar.sh`**:
    *   Script shell para chamadas remotas eficientes.

---

### 🧪 Sprint 5 (Pendentes) — Qualidade e Validação Automática

#### 👨‍🔬 Responsabilidade: `test-engineer` (S5.1, S5.5), `backend-specialist` (S5.2, S5.3) e `devops-engineer` (S5.4)

*   **[S5.1] Cobertura de Testes Unitários**:
    *   Escrever `core/tests/test_validadores.py` cobrindo pelo menos 15 cenários de Markdown válido/inválido.
*   **[S5.2 & S5.3] Detecção de Modo de Aula**:
    *   Implementar `detectar_modo(texto: str) -> str` e exibi-lo como coluna calculada no Django Admin.
*   **[S5.4] Hook pre-commit**:
    *   Configurar hook para validação local de arquivos `.md` modificados antes de registrar commits.

---

### 💎 Sprint 6 (Pendentes) — UX do Dashboard

#### 👨‍💻 Responsabilidade: `frontend-specialist` (S6.1-S6.7)

*   **[S6.1] Toggle de Tema Persistente**:
    *   Salvar preferência de tema via `localStorage`.
*   **[S6.2 & S6.3] Anchor Links & Copy Code**:
    *   Implementar botões rápidos de copiar e IDs automáticos nos cabeçalhos e blocos de código.
*   **[S6.4] Barra de Progresso**:
    *   Feedback visual de leitura no topo da página.
*   **[S6.5] Sumário Lateral Opcional**:
    *   Layout lateral reativo para telas grandes.
*   **[S6.6 & S6.7] Ajustes Finais de Layout & Impressão**.

---

## 📈 Ordem Recomendada de Execução

```
[Planejamento (Fase 1)] 
         ↓
[S2.7 & S2.8] (Lógica de validação base)
         ↓
[S5.1 & S5.2] (Testes unitários e heurística de modo)
         ↓
[S2.4, S2.5 & S2.6] (CSS/JS e colapso de código longo)
         ↓
[S3.7 & S3.8] (Validações visuais da Apostila)
         ↓
[S4.1 a S4.5] (API, CLI, tokens de autenticação e Hermes)
         ↓
[S6.1 a S6.7] (Melhorias de UX, tema, cópia e progresso)
```

---

## 🛑 Critério de Aceitação (DoD Geral)

1. Testes unitários rodando e passando via `pytest`.
2. Sem violações graves de linter no código Python adicionado/modificado.
3. Sem vulnerabilidades detectadas nas dependências ou exposição de segredos (`security_scan.py`).
4. Scripts de validação global executados com sucesso.
