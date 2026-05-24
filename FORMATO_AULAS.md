# FORMATO_AULAS.md — Fonte de verdade do formato de aulas

**Versão 2.1** · Atualizado em 2026-05-24

> Este documento substitui `AULAS_SPEC.md` e `formato_ideal.md`.
> Todos os geradores (Claude Desktop, Hermes Agent, CoimbraBot, Claude Code) seguem este formato.
> O ProfessorDash (`aulas.tonicoimbra.com`) é a fonte de verdade da renderização.
> O parser real está em `core/markdown_extensions.py` — qualquer divergência entre este documento e o parser, o parser vence e este documento deve ser corrigido.

---

## 0. TL;DR para o agente

Antes de gerar qualquer aula:

1. Identificar o **modo**: `conceitual`, `prático` ou `apostila`.
2. Seguir o **contrato do renderer** (seção 2).
3. Usar a **sintaxe canônica `:::tipo`** para todos os componentes (seção 3).
4. Aplicar o **template do modo** (seções 5, 6 e 7).
5. Validar com o **checklist** (seção 9).

A sintaxe canônica é `:::tipo`. HTML bruto funciona apenas como fallback documentado (seção 3.9) e é desencorajado.

---

## 1. Modos de aula

### 1.1 Conceitual

Para aulas que apresentam definições, teorias, processos ou comparações.
Estrutura: exposição → analogia → fixação → atividade.

### 1.2 Prático

Para aulas em que o aluno **constrói algo** (codifica, modela, configura).
Estrutura: objetivo → pré-requisito → passo a passo → checkpoint → erro comum → desafio.

### 1.3 Apostila

Para material de leitura extensa, distribuído em HTML standalone fora do dashboard.
Estrutura: igual conceitual ou prático, mas renderizado via `templates/aulas/apostila.html`. O Markdown **não muda** entre dashboard e apostila — muda só o renderer.

---

## 2. Contrato obrigatório do renderer

Estes requisitos valem para todos os modos. Quebrá-los faz a apresentação falhar.

### 2.1 Título

Cada aula começa com um único `#` no topo.

```
# Aula 07 — Persistência com localStorage
```

### 2.2 Introdução obrigatória

O primeiro bloco útil após o `#` é um **parágrafo simples** de 3 a 6 linhas. Não pode ser lista, citação, bloco `:::`, tabela ou estar dentro de `<div>`.

### 2.3 Seções `##`

São a estrutura real da agenda e do modo apresentação. Cada `##` vira um slide.

- Faixa ideal: **4 a 6 seções `##`**.
- Máximo: 8.
- A capa da apresentação mostra os 6 primeiros `##`.

### 2.4 Subtítulos `###`

Apenas como subtítulo dentro de uma seção `##`.

### 2.5 Top-level limpo

`#`, parágrafo introdutório, `##` e `---` precisam ser **filhos diretos** do Markdown. Nunca dentro de wrappers HTML.

### 2.6 Limite por slide

O modo apresentação agrupa até **4 elementos top-level** por slide dentro de uma seção `##`. Listas, tabelas e blocos de código contam como **1 elemento cada**.

### 2.7 Sem frontmatter

Nunca incluir bloco `--- ... ---` no topo. Metadados ficam no banco do ProfessorDash.

---

## 3. Sintaxe canônica — blocos `:::`

A extensão `core/markdown_extensions.py` reconhece blocos delimitados por `:::tipo ... :::`. Esta é a sintaxe **obrigatória** para todos os componentes interativos.

### 3.1 Anatomia geral

```
:::tipo Título opcional na mesma linha
Conteúdo do bloco.
Mais texto.
:::
```

- O nome do tipo vem **imediatamente após** os três dois-pontos, sem espaço (`:::dica`, não `::: dica`).
- Tudo que vem depois do tipo, na **mesma linha**, é interpretado como **título customizado** (sobrescreve o padrão).
- Cada bloco termina com `:::` em uma linha própria.

### 3.2 Tipos de callout suportados (8)

| Tipo `:::`        | Cor       | Título padrão | Ícone | Uso canônico                                  |
| ----------------- | --------- | ------------- | ----- | --------------------------------------------- |
| `:::objetivo`     | `c-green` | Objetivo      | 🎯    | Objetivo da aula, entrega, checkpoint         |
| `:::importante`   | `c-amber` | Importante    | ⚠️    | Atenção, cilada, comparação crítica           |
| `:::dica`         | `c-blue`  | Dica          | 💡    | Dica prática, sugestão                        |
| `:::exemplo`      | `c-violet`| Exemplo       | 📝    | Exemplo concreto, demonstração                |
| `:::atencao`      | `c-coral` | Atenção       | 🚨    | **Erro comum**, cuidado, depreciação          |
| `:::conceito`     | `c-blue`  | Conceito      | 📖    | Definição, conceito-chave                     |
| `:::exercicio`    | `c-violet`| Exercício     | ✍️    | Exercício de fixação não-interativo           |
| `:::curiosidade`  | `c-blue`  | Curiosidade   | 🔍    | Contexto histórico, fato interessante         |

**Importante:** o autor **não escolhe a cor diretamente** — escolhe o propósito (`:::dica`, `:::conceito`) e a cor vem com o tipo. Isso garante consistência visual entre aulas.

### 3.3 Bloco genérico (callout simples)

```
:::dica
A função `console.log()` é sua melhor amiga para depurar.
Use-a sempre que precisar inspecionar valores em tempo real.
:::
```

Renderiza como callout azul com título "Dica".

### 3.4 Com título customizado

```
:::conceito DOM — Document Object Model
Representação da página HTML como uma árvore de objetos JavaScript,
onde cada elemento vira um nó manipulável.
:::
```

Renderiza com título "DOM — Document Object Model" em vez do padrão "Conceito".

### 3.5 Questão interativa

```
:::questao Qual método remove um item específico do localStorage?
a) localStorage.delete("chave")
b) localStorage.removeItem("chave") *
c) localStorage.remove("chave")
d) delete localStorage["chave"]
> O método correto é removeItem(). delete() não existe e remove()
> não está padronizado. O acesso via delete operator funciona em
> alguns navegadores mas é desencorajado.
:::
```

Regras técnicas:

- O **enunciado vem na mesma linha** do `:::questao`, depois do tipo.
- Alternativas no formato `a) texto`, `b) texto`, `c) texto`, `d) texto`.
- A **correta tem ` *`** (espaço + asterisco) **no final da linha**.
- O gabarito começa com `>` na primeira linha; linhas seguintes do gabarito não precisam de `>`.
- O `data-idx` é gerado automaticamente como `q-1`, `q-2`... (com hífen).

Regras editoriais:

- **Exatamente 2 questões por aula** no modo conceitual.
- 0 a 2 no modo prático.
- Letra correta deve variar entre Q1 e Q2.
- Q1: aplicação direta. Q2: formato negativo ("NÃO é", "EXCETO") ou identificação de erro.
- Gabarito mínimo 2 linhas, explicando o motivo.

### 3.6 Roteiro do professor

```
:::roteiro
Pessoal, façam um teste mental: imagine um site de cadastro que,
ao clicar em 'Enviar', recarrega a página inteira e apaga tudo.
Nosso trabalho é impedir exatamente isso.
:::
```

Regras:

- Cabeçalho fixo (🎙️ Roteiro de fala), não pode customizar.
- `.roteiro` **não entra** no modo apresentação.
- No máximo 1 por aula.
- Não carrega conteúdo essencial.

### 3.7 Resumo final

```
:::resumo
- Persistência de dados é manter informações entre execuções
- localStorage usa pares chave-valor e só armazena strings
- JSON.stringify converte objetos em texto antes de salvar
- Próxima aula: introdução ao SQLite local
:::
```

Renderiza como `<ul class="resumo-list">` com checkmarks verdes. Os `-`, `*` ou `1.` no início das linhas são removidos automaticamente.

### 3.8 Limitações de conteúdo dos blocos `:::`

**Crítico:** o conteúdo dentro de blocos `:::` é tratado como **texto plano com quebras de linha preservadas** (`<br>`). Isso significa que dentro de um bloco `:::`:

- **Não funciona:** `**negrito**`, `*itálico*`, `` `código inline` ``, listas Markdown, links `[texto](url)`, HTML bruto como `<strong>`, blocos de código indentados.
- **Funciona:** texto puro, com quebras de linha que viram `<br>`.

Para incluir **código** próximo de um callout, coloque o bloco de código **fora** do `:::`, como elemento Markdown normal:

```
:::importante
O método setItem aceita só strings. Para salvar objetos, use
JSON.stringify antes.
:::

```js
localStorage.setItem("alunos", JSON.stringify(lista));
```
```

Para **destacar termos** dentro de um callout, use o **título customizado** (que aceita formatação visual via CSS) e mantenha o corpo descritivo.

### 3.9 HTML bruto como fallback (desencorajado)

O markdownx aceita HTML inline fora dos blocos `:::`. Você pode usar HTML para casos não cobertos pela extensão, mas:

- Você **perde o título automático e o ícone** (precisa escrever todos).
- Você **perde a consistência visual** garantida pelos tipos.
- O modo apresentação **pode quebrar** se o HTML estiver mal formado.

**Use HTML apenas se a extensão não cobrir o caso.** Em todos os outros cenários, use `:::tipo`.

### 3.10 Referências (opcional)

Bloco de referências bibliográficas no fim, fora dos `:::`:

```html
<button class="refs-toggle" onclick="this.nextElementSibling.classList.toggle('open')">📚 Referências</button>
<div class="refs-content">
 <ul>
  <li>AUTOR, Nome. <strong>Título</strong>. Editora, Ano.</li>
 </ul>
</div>
```

Não entra no modo apresentação.

---

## 4. Estrutura recomendada por modo

### 4.1 Modo conceitual (5 a 6 seções `##`)

1. `# Aula XX — Título`
2. Parágrafo introdutório (sem `:::`).
3. `## Conceito central` (com `:::conceito` ou `:::dica`)
4. `## Comparação ou contraste` (com `:::importante`)
5. `## Exemplo prático` (com `:::exemplo` + opcional `:::curiosidade`)
6. `## Questões de fixação` (2 `:::questao`)
7. `## Atividade prática` (com `:::objetivo` para entrega)
8. `## Fechamento` (com `:::resumo`)

### 4.2 Modo prático (6 a 7 seções `##`)

1. `# Aula XX — Título`
2. Parágrafo introdutório.
3. `## O que vamos construir` (com `:::objetivo`)
4. `## Pré-requisitos` (com `:::dica` ou `:::conceito`)
5. `## Passo a passo` (texto + blocos de código curtos)
6. `## Checkpoint` (com `:::objetivo`)
7. `## Erros comuns` (com 1 ou 2 `:::atencao`)
8. `## Desafio` (com `:::importante` para desafio extra)
9. `## Código completo` (opcional, no fim — bloco único)
10. `## Fechamento` (com `:::resumo`)

> Questões viram opcionais no modo prático. Se a aula tem conceito embutido (ex.: o que é JSON), mantenha as 2. Se é puramente execução, omita.

### 4.3 Modo apostila

Estrutura igual ao modo conceitual ou prático. O mesmo Markdown é processado pelo template `templates/aulas/apostila.html`, que adiciona hero, sumário lateral, toggle de tema, anchor links, progress bar e modo impressão.

---

## 5. Template do modo conceitual

```markdown
# Aula XX — [Título]

[Parágrafo introdutório de 3 a 6 linhas. Sem :::.]

## [Conceito central]

:::conceito [Termo central]
Definição clara e objetiva do conceito. Pode ter quebras de linha
que viram <br>, mas não use Markdown interno.
:::

[Parágrafo explicativo curto.]

## [Comparação ou contraste]

:::importante [A] vs [B]
Diferenciação importante. Quando usar cada um.
:::

## [Exemplo prático]

:::exemplo [Caso real]
Exemplo concreto da aplicação do conceito.
:::

:::curiosidade Origem histórica
Contexto histórico ou fato interessante.
:::

## Questões de fixação

:::questao [Enunciado da questão 1, aplicação direta]
a) [Alternativa A]
b) [Alternativa B] *
c) [Alternativa C]
d) [Alternativa D]
> Explicação objetiva do gabarito em pelo menos 2 linhas,
> mostrando por que B é a resposta certa e o que torna as
> outras incorretas.
:::

:::questao [Enunciado da questão 2, formato negativo]
a) [Alternativa A]
b) [Alternativa B]
c) [Alternativa C] *
d) [Alternativa D]
> Explicação detalhada de por que C é a alternativa que NÃO
> se enquadra no conceito apresentado.
:::

## Atividade prática

[Descrição da atividade em até 15 minutos.]

:::objetivo Entrega
Formato de entrega esperado, nome do arquivo sugerido, prazo.
:::

:::roteiro
Fala do professor em primeira pessoa, tom conversacional, com
pausas naturais. Não carrega conteúdo essencial — só guia a aula.
:::

## Fechamento

:::resumo
- [Ponto 1 do que foi visto]
- [Ponto 2 do que foi visto]
- [Ponto 3 do que foi visto]
- Próxima aula: [gancho de 1 linha]
:::
```

---

## 6. Template do modo prático

```markdown
# Aula XX — [Título da construção]

[Parágrafo introdutório de 3 a 6 linhas. Sem :::.]

## O que vamos construir

[2 a 4 linhas descrevendo o resultado visível ao final da aula.]

:::objetivo Resultado final
O que o aluno vai ver funcionando ao final dos 50 minutos.
:::

## Pré-requisitos

:::dica Para esta aula você precisa de
Editor de código aberto, navegador moderno, arquivo X salvo na
pasta da aula anterior.
:::

## Passo a passo

1. **[Verbo de ação]** — [explicação de 1 linha].

```html
<form id="contato">
 <input name="email" type="email" required>
 <button type="submit">Enviar</button>
</form>
```

2. **[Verbo de ação]** — [explicação].

```js
const form = document.getElementById('contato');
form.addEventListener('submit', (e) => {
 e.preventDefault();
 console.log('Enviado');
});
```

3. **[Verbo de ação]** — [explicação].

```js
const dados = new FormData(form);
console.log(Object.fromEntries(dados));
```

## Checkpoint

:::objetivo Você está no caminho certo se
Ao recarregar a página e digitar um email no campo, o console
do navegador mostra um objeto com a propriedade email preenchida.
:::

## Erros comuns

:::atencao Sintoma: a página recarrega ao clicar em Enviar
Causa: faltou o preventDefault no listener do submit.
Correção: garanta que a primeira linha do listener é
event.preventDefault().
:::

:::atencao Sintoma: console mostra "[object Object]" em vez dos dados
Causa: o FormData não é um objeto comum — precisa ser convertido.
Correção: use Object.fromEntries(formData) ou Array.from(formData).
:::

## Desafio

[1 ou 2 modificações no código pronto, não refazer do zero.]

:::importante Desafio extra
Para quem terminar primeiro: adicione validação de email que
verifique se contém arroba e ponto antes do envio.
:::

:::roteiro
Pessoal, esse erro do preventDefault é o número 1 de quem começa
com formulários em JavaScript. Vou repetir três vezes na aula
porque é o que mais aparece em prova prática.
:::

## Código completo

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
 <meta charset="UTF-8">
 <title>Formulário de contato</title>
</head>
<body>
 <form id="contato">
  <input name="email" type="email" required>
  <button type="submit">Enviar</button>
 </form>
 <script>
  const form = document.getElementById('contato');
  form.addEventListener('submit', (e) => {
   e.preventDefault();
   const dados = new FormData(form);
   console.log(Object.fromEntries(dados));
  });
 </script>
</body>
</html>
```

## Fechamento

:::resumo
- Capturamos dados de formulário com FormData
- preventDefault impede o recarregamento padrão
- Object.fromEntries converte FormData em objeto JS
- Próxima aula: persistindo os dados com localStorage
:::
```

---

## 7. Template do modo apostila

Apostila usa **o mesmo Markdown** do modo conceitual ou prático. A diferença é o renderer (`templates/aulas/apostila.html`), que adiciona:

- Hero com título, eyebrow e meta-grid.
- Sumário lateral fixo (TOC) com scroll spy.
- Barra de progresso de leitura.
- Toggle de tema claro/escuro com persistência.
- Anchor links em `h2` e `h3`.
- Botão "voltar ao topo".
- Copy-to-clipboard nos blocos de código.
- Modo impressão refinado (A4).

Para a apostila ficar boa, o Markdown precisa:

- Ter parágrafos descritivos (não só `:::`).
- Ter pelo menos 5 seções `##`.
- Ter blocos de código completos ou seção `## Código completo`.
- Ter `:::curiosidade` para enriquecer o contexto.

---

## 8. Importação automática no ProfessorDash

```
POST /turmas/<pk>/aulas/importar/
```

Aceita upload de `.md` via multipart/form-data, campo `arquivo`.

```bash
curl -X POST https://aulas.tonicoimbra.com/turmas/<pk>/aulas/importar/ \
 -H "Authorization: Token $TOKEN" \
 -F "arquivo=@aula-07.md"
```

Após a importação:

1. Strip do frontmatter YAML, se houver.
2. Renderização pelo `django-markdownx` com a extensão `professordash_blocks`.
3. Aplicação do CSS de `aula_detalhe.html`.

---

## 9. Checklist final por aula

- [ ] Um único `#` no topo.
- [ ] Parágrafo simples logo abaixo do `#`, sem `:::` e sem HTML.
- [ ] Entre 4 e 6 seções `##` (até 8 em casos extremos).
- [ ] `##` e `---` não estão dentro de wrappers HTML.
- [ ] Nenhuma lista Markdown com mais de 5 itens dentro de uma seção principal.
- [ ] Nenhum bloco de código com mais de 20 linhas dentro de seção principal (use `## Código completo` no fim).
- [ ] Componentes interativos usam **sintaxe `:::tipo`**, não HTML bruto.
- [ ] Conteúdo dos blocos `:::` é texto plano (sem `**bold**`, sem listas, sem HTML interno).
- [ ] Código fica **fora** dos blocos `:::`, em fences Markdown normais.
- [ ] Exatamente 2 `:::questao` (modo conceitual) ou 0 a 2 (modo prático).
- [ ] Cada questão tem exatamente uma alternativa com ` *` no final.
- [ ] Cada questão tem `>` no início da primeira linha de gabarito.
- [ ] Letra correta varia entre Q1 e Q2.
- [ ] Cada gabarito tem mínimo 2 linhas de explicação.
- [ ] No máximo 2 callouts por seção `##`.
- [ ] `:::atencao` usado apenas para erros/cuidado.
- [ ] `:::roteiro` presente (no máximo 1) e sem conteúdo essencial.
- [ ] `:::resumo` no fechamento com 3 a 4 itens, incluindo gancho da próxima aula.

---

## 10. Migração de aulas antigas (v1 → v2.1)

Para aulas escritas antes desta versão usando HTML bruto, a tradução é:

| Antigo (HTML)                                       | Novo (`:::tipo`)        |
| --------------------------------------------------- | ----------------------- |
| `<div class="callout c-green">` (objetivo, entrega) | `:::objetivo`           |
| `<div class="callout c-blue">` (dica, conceito)     | `:::dica` ou `:::conceito` |
| `<div class="callout c-amber">` (atenção, comparação)| `:::importante`         |
| `<div class="callout c-violet">` (exemplo, analogia)| `:::exemplo`            |
| `<div class="callout c-coral">` (erro, cuidado)     | `:::atencao`            |
| `<div class="callout c-blue">` (curiosidade)        | `:::curiosidade`        |
| `<div class="roteiro">`                             | `:::roteiro`            |
| `<div class="callout c-green">` + `<ul class="resumo-list">` | `:::resumo`     |
| `<div class="questao" data-idx="q1">`...            | `:::questao Enunciado?` + alternativas com `*` |

Não é obrigatório migrar aulas existentes — elas continuam funcionando via fallback HTML. Mas toda aula **nova** deve usar `:::tipo`.

---

## 11. Prompt curto para agentes

> Gere uma aula em Markdown com um único `#` no topo, um primeiro parágrafo simples logo abaixo, 4 a 6 seções `##` como estrutura principal, e use a sintaxe canônica `:::tipo` para todos os componentes interativos. Tipos disponíveis: `:::objetivo` `:::importante` `:::dica` `:::exemplo` `:::atencao` `:::conceito` `:::exercicio` `:::curiosidade` `:::roteiro` `:::resumo` `:::questao`. O conteúdo dos blocos é texto plano com quebras de linha — não use Markdown interno. Para código, use fences Markdown fora dos blocos `:::`. Exatamente 2 questões em modo conceitual (0 a 2 em prático). `:::atencao` é reservado para erros e cuidados. `:::roteiro` no máximo 1 por aula, sem conteúdo essencial. Sempre termine com `:::resumo` incluindo gancho da próxima aula. Aplique o checklist da seção 9 antes de entregar.

---

## 12. Versionamento

| Versão | Data       | Mudanças                                                                                       |
| ------ | ---------- | ---------------------------------------------------------------------------------------------- |
| 2.1    | 2026-05-24 | Adota `:::tipo` como sintaxe canônica. Documenta os 8 tipos da extensão. Documenta limitação de conteúdo (texto plano). HTML bruto vira fallback desencorajado. Migração antiga em seção dedicada. |
| 2.0    | 2026-05-24 | Fusão de AULAS_SPEC.md + formato_ideal.md. Inclusão dos 3 modos. (Continha erro: documentava HTML bruto como canônico, quando a sintaxe canônica é `:::tipo`.) |
| 1.x    | —          | Versões em AULAS_SPEC.md e formato_ideal.md (deprecados).                                       |
