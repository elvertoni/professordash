# Formato ideal para aulas em `.md`

Este arquivo define o contrato esperado para aulas em Markdown no ProfessorDash.

Objetivo:
- funcionar bem na leitura normal
- funcionar bem no modo apresentacao
- evitar que o renderer quebre hero, agenda, secoes ou questoes

O ponto central e simples: o renderer depende de alguns elementos estruturais exatos. Entao o agente deve seguir este formato com disciplina.

---

## 1. Contrato obrigatorio do renderer

### 1.1 Titulo

Toda aula deve comecar com um unico `#`.

Exemplo:

```md
# Aula 07 - Tema da aula
```

O primeiro `#` e removido da renderizacao do corpo e usado como titulo principal da aula. Nao repita outro `#` depois.

### 1.2 Intro obrigatoria

O primeiro bloco util logo abaixo do `#` deve ser um paragrafo simples.

Esse paragrafo vira o resumo principal da capa da aula e da abertura da apresentacao.

Regras:
- deve vir imediatamente abaixo do `#`
- deve ser um paragrafo normal
- nao pode ser lista
- nao pode ser quote
- nao pode ser callout
- nao pode ser tabela
- nao pode estar dentro de `<div>`

Bom:

```md
Nesta aula, vamos entender o conceito X, comparar com Y e aplicar isso em um exemplo pratico de sala.
```

Ruim:

```md
> Pergunta provocadora
```

```html
<div class="callout c-blue">...</div>
```

### 1.3 Secoes principais

Cada secao principal da aula deve comecar com `##`.

Essas secoes sao a base real da agenda e do modo apresentacao.

Regras:
- use `4` a `6` secoes `##` como faixa ideal
- `8` e o maximo recomendado
- a capa da apresentacao mostra apenas os `6` primeiros `##`
- cada `##` deve representar uma ideia central

Exemplo:

```md
## O que e X
## X vs Y
## Elementos essenciais
## Exemplo pratico
## Atividade
## Fechamento
```

### 1.4 `###` e subtitulos

Use `###` apenas como subtitulo dentro de uma secao `##`.

`###` ajuda a nomear subslides, mas nao cria nova secao principal.

### 1.5 `---`

`---` pode ser usado como respiro visual, mas nao substitui `##`.

Comportamento tecnico atual:
- se existirem `##`, o renderer usa `##` para segmentar a apresentacao
- `---` vira corte de slide apenas quando nao existem `##`
- `---` no comeco da aula e descartado

Conclusao:
- use `##` como estrutura principal
- use `---` so como separador secundario

### 1.6 Elementos top-level

`#`, intro, `##` e `---` precisam ser filhos diretos do Markdown renderizado.

Nao envolva esses blocos em wrappers arbitrarios como:

```html
<div class="secao">
  <h2>...</h2>
</div>
```

O renderer aceita HTML bruto, mas wrappers errados escondem os elementos estruturais que ele procura.

---

## 2. Como os slides sao montados

O modo apresentacao quebra o conteudo por elementos de bloco top-level.

Regra tecnica importante:
- cada slide agrupa ate `4` elementos por vez dentro da mesma secao

Consequencias:
- uma lista enorme continua contando como `1` elemento e pode explodir o slide
- uma tabela grande continua contando como `1` elemento e pode ficar ilegivel
- um bloco de codigo longo continua contando como `1` elemento e pode ficar ruim
- um unico `<div>` com tudo dentro prejudica a quebra automatica

Por isso, escreva em blocos curtos e separados.

Faixa segura por secao `##`:
- `1` callout forte
- `1` ou `2` paragrafos curtos
- `1` lista curta
- opcionalmente `1` subtitulo `###`

Evite:
- listas com mais de `5` itens
- paragrafos muito longos
- tabelas largas
- blocos de codigo extensos
- varios callouts seguidos sem texto normal entre eles

---

## 3. Componentes suportados

Use HTML apenas nos componentes abaixo. Fora isso, prefira Markdown normal.

### 3.1 Callout

Estrutura canonica:

```html
<div class="callout c-blue">
  <div class="callout-icon">Info</div>
  <div class="callout-body">
    <p class="callout-title">Titulo do callout</p>
    <p class="callout-text">Texto curto do callout.</p>
  </div>
</div>
```

Variantes suportadas:
- `c-blue`
- `c-green`
- `c-amber`
- `c-violet`
- `c-coral`

Regras:
- use a estrutura acima
- `callout-title` e `callout-text` devem existir
- o texto deve ser curto
- prefira `1` callout forte por secao

### 3.2 Questao interativa

Use exatamente esta estrutura:

```html
<div class="questao" data-idx="q1">
  <p class="questao-num">Questao 1</p>
  <p class="questao-enunciado">Texto da questao.</p>
  <ul class="alternativas">
    <li class="alt" data-letra="A"><span class="alt-badge">A</span> Alternativa A</li>
    <li class="alt" data-letra="B"><span class="alt-badge">B</span> Alternativa B</li>
    <li class="alt" data-letra="C" data-correta="true"><span class="alt-badge">C</span> Alternativa correta</li>
    <li class="alt" data-letra="D"><span class="alt-badge">D</span> Alternativa D</li>
  </ul>
  <div class="gabarito">
    <span class="gab-texto">Explicacao objetiva do gabarito.</span>
  </div>
</div>
```

Regras obrigatorias:
- `data-idx` unico por aula: `q1`, `q2`, `q3`...
- exatamente `4` alternativas
- exatamente `1` alternativa com `data-correta="true"`
- toda alternativa precisa de `data-letra`
- toda alternativa precisa de `.alt-badge`
- o gabarito deve conter `.gab-texto`
- o gabarito deve explicar o motivo, nao so repetir a resposta

### 3.3 Roteiro do professor

Use para fala do professor no modo normal.

Estrutura:

```html
<div class="roteiro">
  <div class="roteiro-header">Roteiro de fala do professor</div>
  <p class="roteiro-texto">Texto em primeira pessoa, pronto para fala em sala.</p>
</div>
```

Regra tecnica:
- `.roteiro` nao entra no modo apresentacao

Use assim:
- opcional
- no maximo `1` por aula
- nunca coloque nele o conteudo essencial para entender a aula projetada

### 3.4 Resumo final

Estrutura recomendada:

```html
<div class="callout c-green">
  <div class="callout-icon">Resumo</div>
  <div class="callout-body">
    <p class="callout-title">Resumo da aula</p>
    <ul class="resumo-list">
      <li><span class="resumo-check">OK</span> Ponto 1</li>
      <li><span class="resumo-check">OK</span> Ponto 2</li>
      <li><span class="resumo-check">OK</span> Ponto 3</li>
    </ul>
  </div>
</div>
```

Nao e obrigatorio em termos tecnicos, mas e altamente recomendado.

### 3.5 Referencias

Bloco opcional para leitura normal:

```html
<button class="refs-toggle" onclick="this.nextElementSibling.classList.toggle('open')">
  Referencias
</button>
<div class="refs-content">
  <ul>
    <li>Fonte 1</li>
    <li>Fonte 2</li>
  </ul>
</div>
```

Regras tecnicas:
- `.refs-toggle` e `.refs-content` nao entram na apresentacao
- use no fim da aula
- nao coloque conteudo essencial nesse bloco

---

## 4. Regras editoriais

Escreva para:
- leitura em tela
- apresentacao em TV ou projetor
- aluno de ensino tecnico
- fala oral do professor

Boas praticas:
- 1 ideia central por secao `##`
- blocos curtos
- listas curtas
- linguagem concreta
- exemplos praticos
- comparacoes claras

Evite:
- texto academico denso
- 5 paragrafos longos seguidos
- tabelas complexas
- codigo extenso
- wrappers HTML sem necessidade
- aula inteira composta so de callouts

---

## 5. Estrutura recomendada de aula

Esta sequencia e recomendada, nao obrigatoria:

```md
# Titulo da aula

Paragrafo introdutorio forte.

## Conceito base
Texto curto.

## Comparacao ou contraste
Texto curto + lista curta.

## Exemplo pratico
Exemplo real.

## Questao de fixacao
Questao interativa.

## Atividade
Descricao da atividade.

## Fechamento
Resumo final.
```

---

## 6. Checklist de validacao

Antes de considerar a aula pronta, confirme:

- existe um unico `#` no topo
- existe um paragrafo simples logo abaixo do `#`
- o primeiro paragrafo nao esta dentro de HTML
- existem `4` a `6` secoes `##` bem definidas
- `##` e `---` nao foram usados como wrappers ocultos em HTML
- cada secao `##` tem poucos blocos pesados
- `###` foi usado apenas como subtitulo
- as questoes usam a estrutura exata suportada
- `data-idx` esta unico em toda a aula
- nao ha listas gigantes, tabelas largas ou codigo longo
- `roteiro` e referencias nao carregam conteudo essencial para os slides

---

## 7. Template-base

```md
# Aula XX - [Titulo da aula]

[Paragrafo introdutorio forte com 3 a 6 linhas. Esse texto vira o resumo principal da aula e da capa da apresentacao.]

## [Secao 1]

<div class="callout c-blue">
  <div class="callout-icon">Conceito</div>
  <div class="callout-body">
    <p class="callout-title">[Titulo do conceito]</p>
    <p class="callout-text">[Definicao objetiva e clara]</p>
  </div>
</div>

[Paragrafo explicativo curto.]

## [Secao 2]

[Comparacao, contraste ou lista curta.]

## [Secao 3]

[Exemplo pratico.]

<div class="callout c-violet">
  <div class="callout-icon">Analogia</div>
  <div class="callout-body">
    <p class="callout-title">[Analogia]</p>
    <p class="callout-text">[Analogia concreta e memoravel]</p>
  </div>
</div>

## Questao de fixacao

<div class="questao" data-idx="q1">
  <p class="questao-num">Questao 1</p>
  <p class="questao-enunciado">[Enunciado]</p>
  <ul class="alternativas">
    <li class="alt" data-letra="A"><span class="alt-badge">A</span> [Alternativa A]</li>
    <li class="alt" data-letra="B"><span class="alt-badge">B</span> [Alternativa B]</li>
    <li class="alt" data-letra="C" data-correta="true"><span class="alt-badge">C</span> [Alternativa correta]</li>
    <li class="alt" data-letra="D"><span class="alt-badge">D</span> [Alternativa D]</li>
  </ul>
  <div class="gabarito">
    <span class="gab-texto">[Explicacao do gabarito]</span>
  </div>
</div>

## Atividade pratica

[Descricao da atividade.]

<div class="callout c-green">
  <div class="callout-icon">Entrega</div>
  <div class="callout-body">
    <p class="callout-title">Entrega</p>
    <p class="callout-text">[O que deve ser entregue e em qual formato]</p>
  </div>
</div>

<div class="roteiro">
  <div class="roteiro-header">Roteiro de fala do professor</div>
  <p class="roteiro-texto">[Fala do professor, em primeira pessoa, para o modo normal.]</p>
</div>

## Fechamento

<div class="callout c-green">
  <div class="callout-icon">Resumo</div>
  <div class="callout-body">
    <p class="callout-title">Resumo da aula</p>
    <ul class="resumo-list">
      <li><span class="resumo-check">OK</span> [Ponto 1]</li>
      <li><span class="resumo-check">OK</span> [Ponto 2]</li>
      <li><span class="resumo-check">OK</span> [Ponto 3]</li>
    </ul>
  </div>
</div>

<button class="refs-toggle" onclick="this.nextElementSibling.classList.toggle('open')">
  Referencias
</button>
<div class="refs-content">
  <ul>
    <li>[Fonte 1]</li>
    <li>[Fonte 2]</li>
  </ul>
</div>
```

---

## 8. Prompt curto para o agente

Se precisar resumir tudo em uma instrucao operacional curta:

> Gere uma aula em Markdown com um unico `#` no topo, um primeiro paragrafo simples logo abaixo do titulo, `4` a `6` secoes `##` como estrutura principal, blocos curtos e bons para slide, callouts apenas na estrutura suportada, pelo menos `1` questao interativa valida, e sem envolver `#`, intro ou `##` em wrappers HTML. Use `roteiro` e `referencias` apenas como blocos auxiliares, nunca como conteudo essencial para a apresentacao.
