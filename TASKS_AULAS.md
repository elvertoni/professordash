# TASKS — Gerador de Aulas com IA
**Módulo: ProfessorDash · Admin Only · MVP**

---

## Sprint 0 — Fundação (infra, dependências, Django app)

- [x] Adicionar dependências ao `requirements/base.txt`: `python-pptx`, `python-docx`, `pdfplumber`, `newspaper3k`, `beautifulsoup4`, `openai`
- [x] Adicionar `OPENROUTER_API_KEY` ao `.env.example` e ao `config/settings/base.py`
- [x] Criar app Django `gerador/` com estrutura completa de arquivos
- [x] Registrar `gerador` em `INSTALLED_APPS`
- [x] Criar `gerador/urls.py` e incluir em `config/urls.py` sob `/painel/gerador/`
- [x] Mover/integrar extratores existentes de `gerador_aulas/` para `gerador/extractors/`
- [x] Criar migration inicial com os models `SessaoGeracao` e `MaterialEntrada`
- [x] Verificar que `gerador_aulas/` (módulo legado) pode ser removido após migração — nenhum import ativo encontrado

---

## Sprint 1 — Extração de conteúdo (camada de dados)

- [x] Implementar `extractors/pdf.py` — extração via `pdfplumber` (texto por página)
- [x] Implementar `extractors/pptx.py` — título, corpo e notas de cada slide
- [x] Implementar `extractors/docx.py` — parágrafos limpos do documento
- [x] Implementar `extractors/url.py` — extração via `newspaper3k` / `BeautifulSoup`
- [x] Implementar `extractors/rco.py`:
  - [x] `detectar_papel_rco(filename)` — identifica `slides` / `atividade` / `pratica` pelo nome
  - [x] `extrair_rco(arquivos)` — orquestra extração dos 3 arquivos com seus papéis
  - [x] `montar_conteudo_rco(conteudo)` — consolida conteúdo estruturado por papel
- [x] Garantir que papel `ATIVIDADE` → seção 12 e papel `PRATICA` → seção 11 (nunca inverter)
- [x] Escrever testes unitários para cada extrator (fixtures com arquivos reais)

---

## Sprint 2 — Provider IA e Prompts

- [x] Implementar `providers.py` com cliente OpenRouter (SDK OpenAI-compatível)
- [x] Configurar mapa de modelos: `claude` → `anthropic/claude-sonnet-4-5`, `gemini` → `google/gemini-2.5-pro`, `gpt4o` → `openai/gpt-4o`
- [x] Implementar `gerar_aula(system, user, provider)` → retorna `(markdown, tokens)`
- [x] Implementar `prompts.py`:
  - [x] `SYSTEM_PROMPT` — persona ProfLobster com 15 seções obrigatórias
  - [x] `prompt_rco(slides, atividade, pratica, ...)` — Modo A
  - [x] `prompt_planejar(conteudo, num_aulas, ...)` — Modo B planejamento (resposta JSON)
  - [x] `prompt_aula_livre(aula, total, conteudo, ...)` — Modo B geração individual
- [x] Validar resposta JSON do planejamento (campos `tema_central`, `fio_condutor`, `observacoes`, `aulas`)
- [x] Testar geração com cada provider e verificar estrutura das 15 seções

---

## Sprint 3 — Pipeline e Views

- [x] Implementar `pipeline.py`:
  - [x] `executar_modo_rco(sessao)` — gera 1 aula, salva como rascunho, atualiza tokens
  - [x] `executar_modo_livre(sessao)` — geração em lote com `yield` para SSE
  - [x] `juntar_conteudo(materiais)` — concatena extrações com separadores de fonte
  - [x] `extrair_titulo(markdown)` — extrai título da aula gerada
- [x] Implementar views (`views.py`) com `ProfessorRequiredMixin`:
  - [x] `GeradorIndexView` — GET `/painel/gerador/` (tela principal)
  - [x] `UploadMaterialView` — POST `/painel/gerador/upload/` (upload + extração + cria sessão)
  - [x] `PlanejarView` — POST `/painel/gerador/planejar/` (análise Modo Livre)
  - [x] `AprovarPlanejamentoView` — POST `/painel/gerador/<id>/aprovar/`
  - [x] `GerarAulasView` — GET `/painel/gerador/<id>/gerar/` (SSE streaming)
  - [x] `PreviewAulaView` — GET `/painel/gerador/<id>/preview/<n>/`
  - [x] `SalvarAulasView` — POST `/painel/gerador/<id>/salvar/` (publica rascunhos)
  - [x] `HistoricoView` — GET `/painel/gerador/historico/`
- [x] Registrar todas as URLs em `gerador/urls.py`
- [x] Garantir aulas salvas com `realizada=False` (rascunho editável) associadas à turma correta

---

## Sprint 4 — Interface (templates)

- [x] Criar `templates/gerador/index.html` — tela principal:
  - [x] Seletor de modo: RCO vs. Livre (Alpine.js)
  - [x] Seção Modo RCO: 3 dropzones (PPT obrigatório, Atividade obrigatório, Prática opcional)
  - [x] Seção Modo Livre: dropzone multi-arquivo + botões "Adicionar URL" e "Colar texto"
  - [x] Campos comuns: disciplina/turma (dropdown), número de aulas, nível, provider
  - [x] Campo Modo Livre extra: foco (equilibrado / mais teórico / mais prático)
  - [x] Campo de instruções adicionais (textarea opcional)
  - [x] Botão "Gerar Aula" (Modo RCO) / "Analisar Material" (Modo Livre)
- [x] Criar `templates/gerador/planejamento.html` — revisão do planejamento (Modo Livre):
  - [x] Lista de aulas propostas com campos editáveis nos títulos
  - [x] Exibir `tema_central`, `fio_condutor` e `observacoes` da IA
  - [x] Botões "Voltar" e "Aprovar e Gerar Aulas"
- [x] Criar `templates/gerador/gerando.html` — progresso em tempo real:
  - [x] Progress bar com número de aulas concluídas / total
  - [x] Lista de aulas com status: ✅ concluída / ⏳ gerando / ○ pendente
  - [x] Exibir provider, tokens acumulados e custo estimado
  - [x] Botões "Pausar" e "Ver aulas"
- [x] Adicionar link "Gerador de Aulas" ao menu lateral (`_sidebar.html`) para `is_staff`
- [x] Garantir tema escuro / violet consistente com o design system

---

## Critérios de aceite do MVP

**Modo RCO:**
- [x] Sistema reconhece automaticamente o papel de cada arquivo pelo nome
- [x] Extrai todo o conteúdo dos slides, incluindo notas
- [x] Questões do arquivo `ATIVIDADE` usadas fielmente na seção 12
- [x] Conteúdo do arquivo `PRATICA` usado como base da seção 11
- [x] Aula gerada em menos de 60 segundos

**Modo Livre:**
- [x] Upload aceita PDF, PPTX, DOCX, TXT, MD e URL
- [x] Planejamento proposto é coerente com o material enviado
- [x] Professor edita títulos antes de aprovar
- [x] Progress bar atualiza em tempo real via SSE
- [x] Geração em lote funciona de 1 a 20 aulas sem erro

**Ambos:**
- [x] Aulas salvas como rascunhos editáveis na disciplina
- [x] Padrão de 15 seções obrigatórias respeitado em 100% das gerações
- [x] Suporte a Claude, Gemini e GPT-4o via OpenRouter
- [x] Estimativa de tokens e custo exibida ao final

---

*Versão 2.0 — Março 2026*
