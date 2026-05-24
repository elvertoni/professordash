# Changelog

Todas as mudanças relevantes deste projeto são documentadas neste arquivo.
O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o
projeto adota [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [2.0.0-alpha.4] — 2026-05-24

Sprint 3: apostila standalone inicial.

### Adicionado

- Campo `Aula.gera_apostila` com migration `0004_aula_gera_apostila.py`, formulário e coluna/filtro no admin.
- Views `AulaApostilaView` e `AulaApostilaPublicaView`, com renderização do Markdown via `markdownify`, TOC server-side e anchors em `h2/h3`.
- Rotas admin e pública para apostila HTML standalone.
- Botão "Apostila" no detalhe admin da aula, apontando para download com `?download=1`.
- Comando `python manage.py exportar_apostila <aula_id> <output_path>` para gerar HTML standalone via CLI.

### Observação

- Validação runtime com `manage.py check`, GET 200 e download real ficaram pendentes porque o ambiente local atual não tem Django instalado.

---

## [2.0.0-alpha.3] — 2026-05-24

Sprint 2: início do modo prático no renderer.

### Alterado

- `core/templatetags/markdownx.py`: documentado o pipeline real do filtro `markdownify`, incluindo strip de frontmatter e responsabilidade dos templates sobre blocos de código.
- `templates/aulas/aula_detalhe.html`: blocos `<pre>` agora são normalizados no DOM como `pre.code-shell`, com contagem de linhas para preparar a expansão de código longo.
- `templates/aulas/aula_detalhe.html`: adicionado suporte opt-in a seções numeradas via `aula.numbered_sections`.
- `templates/aulas/aula_detalhe.html`: callouts ganharam estados consistentes de hover/highlight; `c-coral` agora tem paridade no modo leitura, apresentação e impressão.
- `templates/aulas/apostila.html`: suporte a `.section[data-numbered="true"]` para numeração opt-in.

### Observação

- A captura visual antes/depois de `S2.2` ficou pendente para validação manual no navegador.

---

## [2.0.0-alpha.2] — 2026-05-24

Sprint 1.5: desbloqueio da S1.6 após correção da sintaxe canônica.

### Alterado

- `FORMATO_AULAS.md` atualizado para v2.1: sintaxe canônica passa a ser `:::tipo`; HTML bruto documentado como fallback desencorajado.
- `coimbraclaw/Skills/coimbraclaw-prof/SKILL.md` substituído pela v2.1: usa `:::tipo` como canônico, referencia `FORMATO_AULAS.md` como fonte de verdade, aponta `core/markdown_extensions.py` como autoridade final em caso de divergência. (S1.6 desbloqueada)
- `CLAUDE.md`: nota de divergência removida; seção "Formato de aulas" atualizada com frase neutra confirmando `:::tipo` como sintaxe canônica.

### Removido

- `SKILL_v2_DRAFT.md` da raiz (promovido a skill oficial).

---

## [2.0.0-alpha.1] — 2026-05-24

Sprint 1 da refatoração v2.0 (ver `PRD_REFATORACAO.md`): consolidação da
documentação do formato de aulas em uma única fonte de verdade.

### Adicionado

- `FORMATO_AULAS.md` na raiz como fonte de verdade do formato de aulas, com os três modos (conceitual, prático e apostila). (S1.1)
- `README.md` na raiz, com seção "Formato de aulas" apontando para `FORMATO_AULAS.md`. (S1.4)
- `CHANGELOG.md` (este arquivo). (S1.8)

### Alterado

- `AULAS_SPEC.md` reduzido a um redirecionamento de 3 linhas para `FORMATO_AULAS.md` (mantido na raiz por compatibilidade de links externos). (S1.2)
- `formato_ideal.md` reduzido a um redirecionamento de 3 linhas para `FORMATO_AULAS.md` (mantido na raiz). (S1.3)
- `CLAUDE.md`: nova subseção "Formato de aulas (fonte de verdade)" com a instrução de ler `FORMATO_AULAS.md` antes de gerar aulas, mais nota de divergência conhecida. (S1.5)
- `PRD_REFATORACAO.md` (Anexo B): comandos `git mv ... docs/_deprecated/` substituídos por nota explicando que os arquivos deprecados permanecem na raiz com redirect de 3 linhas.

### Bloqueado

- **S1.6 — Sincronizar a skill `coimbraclaw-prof`:** bloqueada em 2026-05-24. A skill v2 (`SKILL.md` na raiz) usa HTML bruto para callouts, enquanto a skill atual em `coimbraclaw/Skills/coimbraclaw-prof/SKILL.md` já usa a sintaxe canônica `:::tipo` da extensão `core/markdown_extensions.py`. Substituir agora causaria regressão. Desbloqueio após o sprint intermediário de correção do `FORMATO_AULAS.md`.

### Verificado (sem alteração)

- **S1.7 — `PRD.md` e `SPEC.md`:** verificados em 2026-05-24. Nenhuma referência aos arquivos deprecados e nenhuma descrição de contrato/formato de aula; nenhuma alteração necessária.

### Pendência conhecida

- O `FORMATO_AULAS.md` v2.0 documenta o formato de aulas em **HTML bruto**, mas a **sintaxe canônica** do renderer é `:::tipo` (extensão `core/markdown_extensions.py`); o HTML é fallback. Correção do `FORMATO_AULAS.md` planejada para um sprint intermediário antes do Sprint 2. Essa pendência bloqueia a S1.6.
