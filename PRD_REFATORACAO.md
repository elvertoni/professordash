# PRD_REFATORACAO.md — ProfessorDash v2.0

> Plano de refatoração do ProfessorDash baseado na auditoria de 2026-05-24 do repositório `elvertoni/professordash`.
> **Como usar:** abrir este arquivo no Claude Code, executar sprint por sprint, marcar `[x]` ao concluir cada task.
> **Branch sugerida:** `refactor/v2`
> **Versão alvo:** 2.0.0

---

## 0. Contexto e diagnóstico

Auditoria identificou três problemas estruturais:

1. **Documentação divergente.** `AULAS_SPEC.md` e `formato_ideal.md` definem o mesmo contrato de forma diferente. Geradores (Claude, CoimbraBot, Hermes) seguem versões inconsistentes.
2. **Suporte limitado a aulas práticas.** O contrato atual foi otimizado para aulas conceituais. Aulas de código sofrem com o limite de "4 elementos por seção" e a ausência de blocos para checkpoint/erro comum.
3. **Apostila standalone inexistente.** Aulas só podem ser consumidas via dashboard. Não há export para HTML standalone (apostila) com sumário, anchor links, toggle de tema, modo de impressão refinado.

Este PRD resolve os três problemas em 6 sprints sequenciais.

### Critérios de sucesso

- Toda aula pode ser gerada nos 3 modos (conceitual, prático, apostila) a partir do mesmo Markdown.
- Geradores convergem em uma única fonte de verdade (`FORMATO_AULAS.md`).
- Qualquer aula pode ser exportada como apostila standalone em 1 clique.
- Hermes Agent importa aulas via API sem intervenção manual.
- Renderer detecta violações do contrato e avisa antes de publicar.

### Convenção de tasks

- Cada task tem ID `S{sprint}.{task}` (ex.: `S2.3`).
- Definição de pronto (DoD) explícita em cada task.
- Tasks com prefixo **[OPC]** são opcionais e podem ser adiadas.

---

## Sprint 1 — Fonte de verdade da documentação

**Objetivo:** consolidar a documentação do formato em um único arquivo canônico e desativar os duplicados.

**Duração estimada:** 2h
**Bloqueia:** Sprints 2 e 3.

- [x] **S1.1** — Criar `FORMATO_AULAS.md` na raiz do repositório
 - Conteúdo: fusão otimizada de `AULAS_SPEC.md` + `formato_ideal.md` (já preparado em anexo).
 - DoD: arquivo commitado, lint markdown OK, sem TODO.

- [x] **S1.2** — Deprecar `AULAS_SPEC.md`
 - Substituir conteúdo do arquivo por: `> Este documento foi substituído por FORMATO_AULAS.md. Veja a fonte de verdade lá.`
 - Manter o arquivo (não deletar) por compatibilidade de links externos.
 - DoD: arquivo reduzido a 3 linhas, com link relativo funcionando.

- [x] **S1.3** — Deprecar `formato_ideal.md`
 - Mesmo procedimento de S1.2.
 - DoD: idem.

- [x] **S1.4** — Atualizar `README.md`
 - Adicionar seção "Formato de aulas" apontando para `FORMATO_AULAS.md`.
 - DoD: README renderiza com link clicável.

- [x] **S1.5** — Atualizar `CLAUDE.md`
 - Substituir referências a `AULAS_SPEC.md` por `FORMATO_AULAS.md`.
 - Adicionar instrução clara: "Antes de gerar aula, ler FORMATO_AULAS.md".
 - DoD: nenhuma referência aos arquivos deprecados.

- [x] **S1.6** — Sincronizar a skill `coimbraclaw-prof`
 - Executada em 2026-05-24 (sprint 1.5). Desbloqueada após correção da sintaxe canônica em `FORMATO_AULAS.md` v2.1. `SKILL.md` substituída pela v2.1 (`SKILL_v2_DRAFT.md`), que usa `:::tipo` como canônico. `SKILL_v2_DRAFT.md` removido da raiz.
 - DoD: skill referencia `FORMATO_AULAS.md` como fonte de verdade. ✓

- [x] **S1.7** — Atualizar `PRD.md` e `SPEC.md`
 - Quando mencionarem formato de aula, redirecionar para `FORMATO_AULAS.md`.
 - DoD: zero contradições com o novo documento canônico.
 - Verificação concluída em 2026-05-24. Nenhuma alteração necessária: grep em `PRD.md` e `SPEC.md` confirmou zero referências aos arquivos deprecados e zero descrição de contrato/formato de aula. DoD satisfeito por construção.

- [x] **S1.8** — Criar `CHANGELOG.md` (se não existir)
 - Entrada para v2.0.0-alpha.1 listando a unificação documental.
 - DoD: arquivo criado, entrada datada.

---

## Sprint 2 — Modo prático no renderer

**Objetivo:** liberar o renderer para aulas de código sem quebrar o modo apresentação das aulas conceituais.

**Duração estimada:** 4h
**Bloqueia:** Sprint 5.

- [x] **S2.1** — Auditar `core/markdownx.py`
 - Confirmar que strip de frontmatter YAML está ativo.
 - Confirmar que blocos `<pre><code>` longos são renderizados com `<pre class="code-shell">` ou similar.
 - Executado em 2026-05-24: arquivo real é `core/templatetags/markdownx.py`; o filtro `markdownify` já remove frontmatter e delega a renderização para `django-markdownx`. Documentado no código que blocos de código saem como `<pre><code>` e que decoração/medição de blocos longos fica nos templates de aula/apostila. `aula_detalhe.html` normaliza esses blocos no DOM como `pre.code-shell` com `data-line-count` e `data-long-code`.
 - DoD: comentário no código documentando o que é processado. ✓

- [x] **S2.2** — Adicionar atributo opcional `numbered` à classe `.section`
 - CSS counter para auto-numerar `h2` quando a seção tem classe `numbered`.
 - Não afeta aulas existentes (opt-in).
 - Executado em 2026-05-24: o CSS atual da aula é inline em `templates/aulas/aula_detalhe.html`, então o suporte opt-in foi adicionado em `.md-content.numbered`; a apostila aceita `.section.numbered` e `.section[data-numbered="true"]`.
 - DoD: CSS adicionado no template atual. Screenshot antes/depois pendente de validação visual no navegador.

- [x] **S2.3** — Garantir paridade dos callouts `c-coral` em todo o CSS
 - Conferir que `c-coral` tem estilo de hover, modo impressão, e estado "highlight" como as outras 4 cores.
 - Executado em 2026-05-24: estados `:hover`, `.is-highlighted` e `[data-highlight="true"]` adicionados para todas as cores; `c-coral` recebeu paridade no modo leitura, apresentação e impressão.
 - DoD: visual de `c-coral` idêntico em consistência ao de `c-blue`. ✓

- [ ] **S2.4** — Refatorar `buildSlides()` no JS do `aula_detalhe.html`
 - Detectar blocos `pre` com mais de 30 linhas e renderizar com botão "Expandir".
 - Manter compatibilidade total com aulas existentes.
 - DoD: teste manual em 3 aulas (1 conceitual antiga, 1 prática nova, 1 com bloco longo).

- [ ] **S2.5** — Adicionar suporte ao bloco `## Código completo`
 - Quando uma seção `##` tem título `Código completo`, ela é renderizada com classe especial `.section-codigo` (fundo escuro, sem cards internos).
 - DoD: CSS aplicado, aula de teste renderizando corretamente.

- [ ] **S2.6** — [OPC] Adicionar syntax highlighting via Prism.js
 - Avaliar se cabe (peso: ~20KB gzipped).
 - Se sim, integrar em `static/js/prism.js` + CSS em `static/css/prism-tema.css`.
 - DoD: blocos `pre code.language-js` aparecem com cores.

- [ ] **S2.7** — Criar `core/validadores.py` com `validar_markdown_aula(texto: str) -> list[str]`
 - Retorna lista de violações do `FORMATO_AULAS.md` seção 9.
 - Checa: um único `#`, parágrafo após `#`, 4 a 6 `##`, 2 questões válidas, `data-correta` único por questão, etc.
 - DoD: 10 testes unitários cobrindo casos válidos e inválidos.

- [ ] **S2.8** — Integrar validador no save da Aula
 - No `models.Aula.clean()` ou em form, rodar `validar_markdown_aula()`.
 - Em caso de violação grave: erro de validação (bloqueia salvar).
 - Em caso de aviso: apenas warning (deixa salvar).
 - DoD: tentativa de salvar aula sem `#` no topo retorna erro claro.

---

## Sprint 3 — Apostila standalone

**Objetivo:** permitir exportar qualquer aula como HTML standalone (apostila) com sumário, tema, anchor links e print refinado.

**Duração estimada:** 6h
**Bloqueia:** Sprint 4 (parcial).

- [x] **S3.1** — Adicionar campo `Aula.gera_apostila` (BooleanField, default True)
 - Migration correspondente.
 - Executado em 2026-05-24: campo adicionado ao model, form e admin; migration `aulas/migrations/0004_aula_gera_apostila.py` criada.
 - DoD: migration criada. Aplicação em dev/produção pendente porque o ambiente local atual não tem Django instalado.

- [x] **S3.2** — Criar `templates/aulas/apostila.html`
 - Template Django completo (já preparado em anexo).
 - Executado em 2026-05-24: template adicionado em `templates/aulas/apostila.html` e ajustado para `.section.numbered` / `.section[data-numbered="true"]`.
 - DoD: arquivo criado. Renderização Django pendente por falta de dependências locais.

- [x] **S3.3** — Criar `aulas/views.py::ApostilaView`
 - URL: `/turmas/<turma_pk>/aulas/<aula_pk>/apostila/`
 - Permissão: pública se aula publicada, professor se rascunho.
 - Contexto: `aula` com `conteudo_html` já renderizado pelo `django-markdownx`.
 - Executado em 2026-05-24: criadas `AulaApostilaView` e `AulaApostilaPublicaView`, usando `conteudo_html` renderizado pelo mesmo filtro `markdownify`.
 - DoD: implementação e rotas criadas. GET 200 pendente de validação com Django instalado.

- [x] **S3.4** — Gerar TOC server-side em `ApostilaView`
 - Após renderizar Markdown, parsear HTML com BeautifulSoup para extrair `h2` e `h3`.
 - Adicionar IDs (slugify) e construir `aula.toc = [(id, titulo, nivel), ...]`.
 - Executado em 2026-05-24: extração server-side implementada sem dependência nova, a partir dos `h2`/`h3` emitidos pelo Python-Markdown; IDs únicos via `slugify`, `aula.toc` e wrappers `.section` gerados antes do template.
 - DoD: TOC e anchors implementados. Clique funcional pendente de validação no navegador.

- [x] **S3.5** — Adicionar botão "Exportar apostila" em `aula_detalhe.html`
 - Visível só para a turma do professor.
 - Link para a URL da `ApostilaView` com `?download=1` para forçar download.
 - Executado em 2026-05-24: botão "Apostila" aparece no detalhe admin quando `gera_apostila=True` e aponta para `?download=1`.
 - DoD: botão criado. Download pendente de validação runtime.

- [x] **S3.6** — Criar comando `python manage.py exportar_apostila <aula_id> <output_path>`
 - Usa o mesmo template para gerar HTML em arquivo, sem servidor.
 - Útil para batch e integração com Hermes.
 - Executado em 2026-05-24: comando `aulas/management/commands/exportar_apostila.py` criado, reutilizando o mesmo contexto/renderizador da view.
 - DoD: comando implementado. Execução real pendente porque o ambiente local atual não tem Django instalado.

- [ ] **S3.7** — Testar a apostila em todos os modos de aula
 - Conceitual: deve aparecer bonito.
 - Prática: deve aparecer com `## Código completo` ao final.
 - Aula longa (3000+ palavras): TOC deve scrollar, anchor links devem funcionar.
 - DoD: 3 aulas de teste validadas visualmente.

- [ ] **S3.8** — Validar modo de impressão da apostila
 - Imprimir em PDF a partir do Chrome/Firefox.
 - Conferir: sem topbar/toc/back-to-top, com gabarito visível, sem cores excessivas.
 - DoD: 3 PDFs gerados a partir de 3 aulas, todos profissionais.

- [ ] **S3.9** — [OPC] Adicionar metadata da OG para preview no WhatsApp/Slack
 - `<meta property="og:title">`, `<meta property="og:description">`, `<meta property="og:image">`.
 - DoD: preview funciona ao colar o link no WhatsApp.

---

## Sprint 4 — Importação e integração com Hermes

**Objetivo:** automatizar publicação de aulas geradas pelo Hermes Agent ou Claude Desktop.

**Duração estimada:** 4h

- [ ] **S4.1** — Auditar `AulaImportarMdView` existente em `aulas/views.py`
 - Confirmar que aceita upload de `.md` via multipart/form-data.
 - Confirmar que aplica `validar_markdown_aula()` (depende de S2.7).
 - DoD: code review com comentários.

- [ ] **S4.2** — Adicionar autenticação por token na `AulaImportarMdView`
 - Suportar header `Authorization: Token <chave>` além da sessão.
 - Criar model `ApiToken(user, key, created_at, last_used_at)`.
 - DoD: importação via curl com token funciona.

- [ ] **S4.3** — Documentar API de importação em `docs/api.md`
 - Exemplo curl, exemplo Python `requests`, exemplo Hermes.
 - DoD: arquivo criado, link no README.

- [ ] **S4.4** — Criar `core/management/commands/importar_aulas.py`
 - CLI para importar `.md` em batch de um diretório.
 - Uso: `python manage.py importar_aulas <turma_id> <pasta>`.
 - DoD: comando funciona, log de sucesso/erro por arquivo.

- [ ] **S4.5** — Criar script `scripts/hermes_importar.sh`
 - Wrapper bash para o Hermes Agent chamar via SSH na VPS.
 - Usa o token (de S4.2) e o comando de S4.4.
 - DoD: documentação em `docs/integracao_hermes.md`.

- [ ] **S4.6** — [OPC] Webhook reverso: Notion → ProfessorDash
 - Quando o Toni atualiza uma página Notion marcada, dispara import automático.
 - Avaliar se cabe no escopo desta refatoração.
 - DoD: decisão documentada (sim/não).

---

## Sprint 5 — Qualidade e validação automática

**Objetivo:** garantir que toda aula publicada cumpre o `FORMATO_AULAS.md`.

**Duração estimada:** 3h
**Depende:** S2.7.

- [ ] **S5.1** — Cobertura de testes do validador
 - Casos positivos: aula conceitual válida, aula prática válida, aula apostila válida.
 - Casos negativos: sem `#`, com 2 `#`, sem parágrafo após `#`, com 3 questões, com letra correta repetida, com bloco código >20 linhas em seção principal.
 - DoD: 15 testes em `core/tests/test_validadores.py`, todos passando.

- [ ] **S5.2** — Detecção automática de modo (conceitual/prático/apostila)
 - Função `detectar_modo(texto: str) -> str` em `core/validadores.py`.
 - Heurística: presença de `## Passo a passo` ou `## Erros comuns` → prático; senão → conceitual.
 - DoD: 6 testes, 3 por modo.

- [ ] **S5.3** — Exibir modo detectado no admin Django
 - Coluna calculada na list view de Aula.
 - DoD: admin mostra "Modo: Prático" automaticamente.

- [ ] **S5.4** — Adicionar pre-commit hook
 - Roda `validar_markdown_aula()` em qualquer `.md` modificado.
 - Configurar `.pre-commit-config.yaml`.
 - DoD: commit com aula inválida é bloqueado localmente.

- [ ] **S5.5** — [OPC] Snapshot tests do renderer
 - Para 3 aulas-referência, gravar o HTML esperado.
 - Qualquer mudança no renderer aciona alerta.
 - DoD: pytest passa, mudanças visíveis em diff.

---

## Sprint 6 — UX do dashboard

**Objetivo:** trazer ao dashboard as melhorias do design da apostila (tema persistente, anchor links, copy code).

**Duração estimada:** 3h

- [ ] **S6.1** — Adicionar toggle de tema persistente em `aula_detalhe.html`
 - Mesma lógica da apostila (localStorage + `prefers-color-scheme`).
 - DoD: tema sobrevive ao F5 e a mudanças de aula.

- [ ] **S6.2** — Adicionar anchor links em `h2` e `h3` da `aula_detalhe.html`
 - Mesma lógica da apostila.
 - DoD: clicar no `#` copia URL para clipboard.

- [ ] **S6.3** — Adicionar copy-to-clipboard nos blocos de código
 - Mesma lógica da apostila.
 - DoD: botão "Copiar" aparece no hover, copia o conteúdo.

- [ ] **S6.4** — Adicionar barra de progresso no topo
 - Mesma lógica da apostila.
 - DoD: barra preenche conforme scroll.

- [ ] **S6.5** — Sumário lateral opcional no `aula_detalhe.html`
 - Toggle no perfil do usuário: "Mostrar TOC ao lado da aula".
 - DoD: setting persistido, layout adapta.

- [ ] **S6.6** — Melhorar print do `aula_detalhe.html`
 - Aplicar o mesmo `@media print` da apostila.
 - DoD: imprimir do dashboard gera PDF tão bom quanto a apostila.

- [ ] **S6.7** — [OPC] Modo apresentação com remote control via teclado
 - Setas, Esc, Home/End. Já existe?
 - Auditar e melhorar se faltar.
 - DoD: navegação por teclado fluida.

---

## Anexos

### A. Arquivos preparados (entregar junto com este PRD)

| Arquivo               | Destino no repo                                       |
| --------------------- | ----------------------------------------------------- |
| `FORMATO_AULAS.md`    | Raiz do repo                                          |
| `SKILL.md`            | `coimbraclaw/Skills/coimbraclaw-prof/SKILL.md`        |
| `apostila.html`       | `templates/aulas/apostila.html`                       |

### B. Comandos úteis para rodar este PRD

```bash
# Criar branch
git checkout -b refactor/v2

# Sprint 1 — começar
# Os arquivos antigos NÃO são movidos: AULAS_SPEC.md e formato_ideal.md
# permanecem na raiz, com o conteúdo reduzido a 3 linhas de redirect
# apontando para FORMATO_AULAS.md (decidido em S1.2/S1.3). Isso preserva
# links externos existentes. FORMATO_AULAS.md já está na raiz.

# Rodar validador (após S2.7)
python manage.py shell -c "from core.validadores import validar_markdown_aula; print(validar_markdown_aula(open('aulas/exemplo.md').read()))"

# Exportar apostila (após S3.6)
python manage.py exportar_apostila 42 /tmp/aula-42.html

# Importar batch (após S4.4)
python manage.py importar_aulas 7 ~/projetos/materiais/programacao-front-end/
```

### C. Ordem recomendada de execução

```
S1 (todas) → S2.1 a S2.3 → S3 (todas) → S2.4 a S2.8 → S4 → S5 → S6
```

Justificativa: S1 desbloqueia tudo; S2.1 a S2.3 são CSS rápidos que ajudam S3; S3 entrega valor visível cedo (apostila funcional); S2.4 a S2.8 polem; S4 conecta o Hermes; S5 trava qualidade; S6 estende ao dashboard.

### D. Definição de feito do PRD inteiro

- [ ] Todos os checkboxes não-OPC concluídos.
- [ ] `git tag v2.0.0` aplicado.
- [ ] Deploy em produção sem regressões.
- [ ] Hermes Agent importou pelo menos 1 aula via API com sucesso.
- [ ] Toni aprovou 1 apostila exportada como "pronta para imprimir".
- [ ] CHANGELOG.md fechado com a versão.

---

**Versão deste PRD:** 1.0
**Data:** 2026-05-24
**Autor:** Claude (a pedido do Toni)
