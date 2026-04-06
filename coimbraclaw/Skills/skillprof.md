---
name: skillprof
description: Skill para geração de aulas completas no formato Markdown do ProfessorDash, com blocos :::tipo, questões interativas e publicação via scripts. Pipeline alinhado ao renderer (validador corrigido em 2026-04-05).
updated: 2026-04-05
status: ativa
---

## 1. Identidade e propósito

O agente `skillprof` é a skill definitiva do OpenClaw para planejar, escrever, revisar e preparar aulas no formato Markdown do ProfessorDash.

O foco desta skill é gerar aulas com sintaxe compatível com o renderer real do projeto, isto é, com blocos `:::tipo`, seções em Markdown puro e questões interativas no padrão aceito por `core/markdown_extensions.py`.

O contexto operacional desta skill é o seguinte:

- o ProfessorDash renderiza o campo de aula com `django-markdownx`
- o filtro `|markdownify` processa o Markdown antes da exibição
- a extensão `core/markdown_extensions.py` converte blocos `:::tipo` em HTML rico
- o template `templates/aulas/aula_detalhe.html` define o visual final desses componentes
- os scripts em `coimbraclaw/Skills/coimbraclaw-prof/scripts/` compõem o pipeline de validação e publicação

Esta skill existe para impedir quatro erros recorrentes:

- gerar aula em formato diferente do que o ProfessorDash realmente renderiza
- usar HTML bruto em vez de blocos `:::tipo`
- publicar aula em série ou disciplina errada
- confiar em documentação antiga ou inconsistente com o código atual

Escopo desta skill:

- planejamento de aulas
- geração de uma aula por vez
- uso correto dos blocos especiais
- escrita de questões interativas
- preparação para validação
- documentação do fluxo de publicação

Fonte de verdade lida para esta skill em 2026-04-05:

- `coimbraclaw/Skills/coimbraclaw-prof/SKILL.md`
- `coimbraclaw/Skills/skill.md`
- `coimbraclaw/Skills/coimbraclaw-prof/_meta.json`
- `coimbraclaw/Skills/coimbraclaw-prof/references/repo-layout.md`
- `core/markdown_extensions.py`
- `templates/aulas/aula_detalhe.html`
- `coimbraclaw/Skills/coimbraclaw-prof/scripts/validate_lesson.py`

Observação operacional importante:

Esta skill corrige divergências existentes entre a skill anterior, o renderer, o filtro `markdownify` e o validador atual. Quando houver conflito entre documentação textual e código, o código lido no repositório prevalece.

## 2. Disciplinas e séries disponíveis

Tabela extraída de `coimbraclaw/Skills/coimbraclaw-prof/references/repo-layout.md`.

| Série | Disciplina | Slug da série | Slug da disciplina | Caminho relativo de publicação |
|---|---|---|---|---|
| 1ª série | Análise e Métodos para Sistemas | `1a-serie` | `analise-e-metodos-para-sistemas` | `publicadas/materias/1a-serie/analise-e-metodos-para-sistemas/` |
| 1ª série | Introdução à Computação | `1a-serie` | `introducao-a-computacao` | `publicadas/materias/1a-serie/introducao-a-computacao/` |
| 2ª série | Inovação, Tecnologia e Empreendedorismo | `2a-serie` | `inovacao-tecnologia-e-empreendedorismo` | `publicadas/materias/2a-serie/inovacao-tecnologia-e-empreendedorismo/` |
| 2ª série | Programação Front-End | `2a-serie` | `programacao-front-end` | `publicadas/materias/2a-serie/programacao-front-end/` |
| 3ª série | Programação no Desenvolvimento de Sistemas | `3a-serie` | `programacao-no-desenvolvimento-de-sistemas` | `publicadas/materias/3a-serie/programacao-no-desenvolvimento-de-sistemas/` |
| 3ª série | Análise e Projeto de Sistemas | `3a-serie` | `analise-e-projeto-de-sistemas` | `publicadas/materias/3a-serie/analise-e-projeto-de-sistemas/` |
| Disciplinas extras | Inteligência Artificial | `disciplinas-extras` | `inteligencia-artificial` | `publicadas/materias/disciplinas-extras/inteligencia-artificial/` |

Regras de mapeamento:

- a série e a disciplina devem ser sempre escolhidas dentro desta tabela
- o slug informado aos scripts deve bater exatamente com a tabela
- o arquivo final segue o padrão `aula-XX-titulo-slug.md`
- a publicação final vai sempre para `publicadas/materias/...`

## 3. Fluxo obrigatório

1. Planejamento

Nesta etapa, o agente não gera a aula completa.

O agente:

- interpreta o pedido
- identifica série, disciplina e tema
- sugere a sequência de tópicos ou títulos de aulas
- pede aprovação antes de escrever a Aula 1

Entrega esperada:

- lista curta e ordenada
- sem corpo completo de aula
- sem publicação

2. Aprovação

Nesta etapa, o professor confirma o plano ou ajusta o escopo.

O agente:

- confirma o recorte temático aprovado
- fixa a série e disciplina corretas
- confirma a aula que será gerada agora

Entrega esperada:

- confirmação objetiva do que foi aprovado
- ausência de conteúdo completo antes da aprovação

3. Geração

Nesta etapa, o agente escreve a aula.

O agente:

- gera uma aula por vez
- usa Markdown limpo
- estrutura o conteúdo com `:::tipo`
- cria questões interativas no padrão do renderer
- evita HTML bruto

Entrega esperada:

- aula completa
- título claro
- introdução
- seções pedagógicas coerentes
- fechamento

4. Validação

Nesta etapa, o agente confronta a aula com o contrato real do projeto.

O agente:

- revisa a sintaxe Markdown
- revisa a presença dos blocos necessários
- confere se a aula respeita o contrato do renderer
- confronta a aula com o comportamento real de `validate_lesson.py`
- detecta inconsistências entre renderer e validador antes de tentar publicar

Entrega esperada:

- aula revisada
- nota explícita sobre qualquer incompatibilidade do pipeline

5. Publicação

Nesta etapa, o agente usa os scripts do projeto.

O agente:

- salva o conteúdo em arquivo `.md`
- chama o script de publicação com os argumentos corretos
- informa o caminho publicado
- informa o status da validação
- informa o status de commit e push

Entrega esperada:

- confirmação do arquivo publicado
- caminho final
- resumo do resultado operacional

## 4. Contrato Markdown do ProfessorDash

### 4.1 Regra central

O contrato real do ProfessorDash é definido principalmente por:

- `core/markdown_extensions.py`
- `templates/aulas/aula_detalhe.html`
- `core/templatetags/markdownx.py`
- `coimbraclaw/Skills/coimbraclaw-prof/scripts/validate_lesson.py`

### 4.2 Regra sobre frontmatter YAML

Pedido desta skill:

- frontmatter YAML com os campos `title`, `description`, `order` e `published`

Estado real do código lido:

- `core/templatetags/markdownx.py` remove frontmatter YAML no início do documento antes de renderizar
- `validate_lesson.py` aceita frontmatter YAML como **opcional**: se presente, é removido antes de validar o conteúdo da aula

Conclusão operacional definitiva:

- tanto a renderização web quanto o pipeline de validação aceitam frontmatter no topo do arquivo
- o validador stripa o frontmatter e valida apenas o conteúdo da aula
- portanto, o arquivo pode incluir ou omitir o bloco YAML — ambos os formatos são válidos
- se o fluxo do professor exigir metadados formais, mantê-los como frontmatter YAML é a forma recomendada

### 4.3 Estrutura por blocos `:::tipo`

Os blocos `:::tipo` são a forma nativa de estruturar conteúdo especial no ProfessorDash.

O `ProfessorDashPreprocessor` faz o seguinte:

- detecta blocos `:::tipo`
- converte cada bloco em HTML protegido via `htmlStash`
- injeta classes CSS específicas compatíveis com o template

Consequência:

- `:::tipo` é a forma certa de escrever componentes especiais
- o HTML resultante deve ser produzido pelo renderer, não manualmente pelo autor da aula

### 4.4 HTML direto no Markdown

Regra recomendada por esta skill:

- nunca usar HTML direto no Markdown da aula

Base real do código:

- a skill antiga já proibia HTML bruto
- `core/markdown_extensions.py` foi criado justamente para transformar Markdown simples em HTML rico
- `validate_lesson.py` proíbe explicitamente a tag `<aside>`

Conclusão:

- para consistência editorial e para preservar o contrato do ProfessorDash, não escrever HTML manual
- usar apenas Markdown comum e blocos `:::tipo`

### 4.5 Título e abertura

`validate_lesson.py` exige:

- a primeira linha útil do arquivo deve ser um título H1 no formato `# Título`
- a primeira linha de conteúdo depois do H1 deve ser um parágrafo simples

Isso significa:

- não começar a aula com bloco `:::`
- não começar com lista
- não começar com tabela
- não começar com citação

### 4.6 Seções mínimas

`validate_lesson.py` procura obrigatoriamente:

- `## Questões de fixação`
- `## Atividade prática`
- `## Fechamento`

Observação:

O script também emite warning se houver poucas seções H2.

### 4.7 Questões

No renderer:

- `:::questao` é a sintaxe de autoria
- o renderer transforma isso em HTML com `.questao`, `.alternativas`, `.alt` e `.gabarito`
- o atributo gerado é `data-idx="q-1"`, `data-idx="q-2"`, etc.

No validador atual (corrigido em 2026-04-05):

- ele valida o Markdown fonte diretamente, sem renderizar
- usa regex `^:::questao\s+.+$` para detectar blocos de questão
- exige exatamente 2 blocos `:::questao` por aula
- exige exatamente uma alternativa terminando com ` *` por bloco

Conclusão operacional:

- o contrato do renderer é `:::questao`
- o contrato do validador é `:::questao`
- o pipeline está alinhado: não há conflito entre renderer e validador

### 4.8 Limites de tamanho recomendados

Recomendação editorial definitiva desta skill:

- título: até 80 caracteres
- descrição curta: até 160 caracteres quando usada em metadados auxiliares
- introdução: 1 a 2 parágrafos curtos
- cada bloco `:::tipo`: 3 a 10 linhas úteis
- cada seção H2: 1 objetivo pedagógico claro
- aula completa: preferencialmente entre 700 e 1800 palavras
- questões: enunciado curto, alternativas objetivas, gabarito conciso

Esses limites não são todos impostos por código, mas são coerentes com:

- o layout de leitura do template
- a divisão de slides feita por `buildSlides()`
- a necessidade de leitura clara em tela

## 5. Blocos disponíveis

### 5.1 `:::objetivo`

Sintaxe exata:

```markdown
:::objetivo
Ao final da aula, o estudante será capaz de identificar os elementos centrais do tema.
:::
```

Sintaxe com título customizado suportada pelo código:

```markdown
:::objetivo Meta da aula
Ao final da aula, o estudante será capaz de identificar os elementos centrais do tema.
:::
```

Quando usar pedagogicamente:

- no início da aula
- para deixar explícito o que o aluno deve aprender
- para alinhar expectativa de aprendizagem

O que renderiza visualmente:

- `<div class="callout c-green">`
- layout flexível com `display: flex`
- espaçamento interno de `1rem 1.25rem`
- cantos arredondados
- borda lateral esquerda de `3px`
- título em verde com classe `.callout-title`
- corpo em texto menor com `.callout-text`
- ícone do mapa: `🎯`

Exemplo completo:

```markdown
:::objetivo
Compreender o que é inteligência artificial, reconhecer exemplos do cotidiano e diferenciar IA de automação simples.
:::
```

### 5.2 `:::importante`

Sintaxe exata:

```markdown
:::importante
Nem todo sistema automatizado usa inteligência artificial.
:::
```

Quando usar pedagogicamente:

- para alertas conceituais
- para evitar confusões frequentes
- para reforçar uma ideia nuclear da aula

O que renderiza visualmente:

- `<div class="callout c-amber">`
- fundo âmbar suave
- borda âmbar com lateral de `3px`
- título âmbar
- ícone do mapa: `⚠️`
- texto em `.callout-text` com cor secundária

Exemplo completo:

```markdown
:::importante
Se o sistema apenas repete uma regra fixa, isso não basta para classificá-lo como IA.
:::
```

### 5.3 `:::dica`

Sintaxe exata:

```markdown
:::dica
Peça aos alunos que comparem um chatbot simples com um assistente que aprende com dados.
:::
```

Quando usar pedagogicamente:

- para facilitar compreensão
- para sugerir associação com exemplos cotidianos
- para orientar observação ou estudo

O que renderiza visualmente:

- `<div class="callout c-blue">`
- fundo azulado suave
- borda em azul ciano
- título em azul
- ícone do mapa: `💡`
- visual de cartão horizontal com ícone à esquerda

Exemplo completo:

```markdown
:::dica
Use exemplos próximos da rotina dos alunos, como recomendações de vídeos, filtros de spam e reconhecimento facial no celular.
:::
```

### 5.4 `:::exemplo`

Sintaxe exata:

```markdown
:::exemplo
Um aplicativo de streaming que recomenda filmes com base no histórico do usuário usa técnicas de IA para prever preferências.
:::
```

Quando usar pedagogicamente:

- para concretizar um conceito abstrato
- para transformar definição em caso real
- para conectar teoria e prática

O que renderiza visualmente:

- `<div class="callout c-violet">`
- fundo violeta suave
- borda violeta
- título violeta
- ícone do mapa: `📝`

Exemplo completo:

```markdown
:::exemplo
Quando um aplicativo sugere músicas parecidas com as que você já ouviu, ele está usando dados anteriores para estimar o que você pode gostar no futuro.
:::
```

### 5.5 `:::atencao`

Sintaxe exata:

```markdown
:::atencao
Evite dizer que toda decisão automática é inteligente. Muitas vezes ela apenas segue regras programadas.
:::
```

Quando usar pedagogicamente:

- para corrigir erro comum
- para prevenir generalização indevida
- para marcar um ponto de cuidado

O que renderiza visualmente:

- `<div class="callout c-coral">`
- fundo coral suave
- borda coral com destaque lateral
- título coral
- ícone do mapa: `🚨`

Exemplo completo:

```markdown
:::atencao
Um semáforo com temporizador fixo não aprende com dados; portanto, ele não deve ser tratado automaticamente como exemplo de IA.
:::
```

### 5.6 `:::conceito`

Sintaxe exata:

```markdown
:::conceito
Inteligência artificial é a área da computação dedicada a construir sistemas capazes de executar tarefas que exigem análise, decisão ou previsão.
:::
```

Quando usar pedagogicamente:

- para definição formal
- para estabilizar vocabulário técnico
- para introduzir o núcleo teórico da aula

O que renderiza visualmente:

- `<div class="callout c-blue">`
- mesma base visual dos callouts azuis
- título padrão `Conceito`
- ícone do mapa: `📖`

Exemplo completo:

```markdown
:::conceito
Machine learning é um subcampo da IA no qual modelos aprendem padrões a partir de dados em vez de depender apenas de regras explícitas escritas pelo programador.
:::
```

### 5.7 `:::exercicio`

Sintaxe exata:

```markdown
:::exercicio
Observe três aplicações do seu dia a dia e classifique quais usam dados para prever, recomendar ou reconhecer padrões.
:::
```

Quando usar pedagogicamente:

- em atividade prática
- para fixação ativa
- para produção individual ou em grupo

O que renderiza visualmente:

- `<div class="callout c-violet">`
- mesmo grupo visual violeta
- destaque de cartão com borda violeta
- título padrão `Exercicio`
- ícone do mapa: `✍️`

Exemplo completo:

```markdown
:::exercicio
Em duplas, escolham um aplicativo conhecido e expliquem qual dado ele coleta, que decisão ele toma e por que isso pode ou não ser considerado IA.
:::
```

### 5.8 `:::curiosidade`

Sintaxe exata:

```markdown
:::curiosidade
O termo inteligência artificial foi consolidado em 1956, em um encontro de pesquisadores em Dartmouth.
:::
```

Quando usar pedagogicamente:

- para ampliar repertório
- para aumentar engajamento
- para conectar aula com história ou cultura científica

O que renderiza visualmente:

- `<div class="callout c-blue">`
- cartão azul
- título padrão `Curiosidade`
- ícone do mapa: `🔍`

Exemplo completo:

```markdown
:::curiosidade
Mesmo antes da popularização dos chatbots, a IA já era usada em filtros de spam, sistemas de recomendação e análise de imagens.
:::
```

### 5.9 `:::roteiro`

Sintaxe exata:

```markdown
:::roteiro
Pergunte aos alunos quais aplicativos do celular parecem “pensar”.
Anote no quadro as respostas antes de apresentar a definição formal.
:::
```

Quando usar pedagogicamente:

- para notas de fala do professor
- para orientar a condução oral da aula
- para registrar perguntas disparadoras e transições

O que renderiza visualmente:

- `<div class="roteiro">`
- fundo escuro `var(--surface)`
- borda discreta
- raio grande com `var(--radius-lg)`
- faixa vertical em gradiente violeta/azul criada por `::before`
- cabeçalho em caixa alta com texto `Roteiro de fala`
- corpo em itálico com `.roteiro-texto`

Correção importante baseada no template real:

- o CSS lido não mostra ocultação automática do bloco no modo aluno
- o JavaScript de apresentação exclui `.roteiro` dos slides em `buildSlides()`
- portanto, o comportamento comprovado no arquivo lido é: visível como card no conteúdo renderizado e ignorado na apresentação, não “oculto no modo aluno” por evidência direta do template lido

Exemplo completo:

```markdown
:::roteiro
Antes de definir IA, peça exemplos espontâneos. Depois, retome cada exemplo para classificar coletivamente se há uso de dados, previsão ou simples regra fixa.
:::
```

### 5.10 `:::resumo`

Sintaxe exata:

```markdown
:::resumo
- IA usa dados para reconhecer padrões
- nem toda automação é IA
- exemplos cotidianos ajudam a identificar aplicações reais
:::
```

Quando usar pedagogicamente:

- no fechamento
- para síntese visual do que foi estudado
- para revisão rápida

O que renderiza visualmente:

- `<ul class="resumo-list">`
- lista sem bullets padrão
- cada item vira linha com divisor inferior
- cada item recebe check verde por `.resumo-check`
- texto em `15px` aproximadamente

Detalhe real do parser:

- o parser remove prefixos como `-`, `*` e numeração
- cada linha não vazia vira um item da lista de resumo

Exemplo completo:

```markdown
:::resumo
- IA depende de dados e modelos
- automação simples segue regras fixas
- recomendações e reconhecimento de padrões são bons indícios de IA
:::
```

### 5.11 `:::questao`

Sintaxe exata:

```markdown
:::questao O que caracteriza uma aplicação de inteligência artificial?
a) Executar sempre a mesma regra sem analisar dados
b) Usar dados para reconhecer padrões e apoiar decisões *
c) Exibir uma tela colorida para o usuário
d) Ser executada apenas na internet
> A alternativa correta é a letra B porque IA depende do uso de dados e modelos para estimar, classificar ou recomendar algo.
:::
```

Quando usar pedagogicamente:

- em fixação
- em checagem rápida de compreensão
- em encerramento de seção

O que renderiza visualmente:

- `<div class="questao" data-idx="q-1">` no renderer atual
- rótulo superior `Questao N`
- enunciado com destaque tipográfico
- lista `.alternativas` sem bullets
- cada alternativa vira `<li class="alt">`
- cada opção tem badge circular `.alt-badge`
- ao clicar, a correta recebe classe `.selected`
- se o aluno errar, a escolhida recebe `.wrong`
- o gabarito `.gabarito` fica oculto até receber a classe `.show`

Exemplo completo:

```markdown
:::questao Qual destas situações é um exemplo típico de IA?
a) Uma lâmpada que apenas acende ao ligar o interruptor
b) Um aplicativo que recomenda músicas com base no histórico do usuário *
c) Uma folha de papel com anotações
d) Uma calculadora desligada
> A alternativa correta é a letra B porque há uso de dados anteriores para prever preferência.
:::
```

## 6. Regras para questões interativas

### 6.1 Sintaxe completa linha a linha

Linha 1:

```markdown
:::questao Enunciado da pergunta?
```

Interpretação real:

- `questao` é o tipo do bloco
- o enunciado fica na mesma linha de abertura
- o enunciado é capturado como `inline_arg`

Linha 2 em diante:

```markdown
a) Alternativa A
b) Alternativa B
c) Alternativa C *
d) Alternativa D
```

Interpretação real:

- o parser aceita letras maiúsculas ou minúsculas
- o padrão regex é `^([a-zA-Z])\)\s*(.+?)(\s*\*\s*)?$`
- o `*` opcional no fim marca a correta

Linha de explicação:

```markdown
> Explicação do gabarito
```

Interpretação real:

- a primeira linha começando com `>` inicia o gabarito
- o `>` é removido
- linhas seguintes, mesmo sem `>`, continuam sendo anexadas ao gabarito até o fechamento do bloco

Fechamento:

```markdown
:::
```

### 6.2 Como escrever alternativas

Escreva sempre no padrão:

- `a) Texto`
- `b) Texto`
- `c) Texto`
- `d) Texto`

Boas práticas:

- manter alternativas com tamanho parecido
- evitar pistas óbvias
- usar linguagem direta
- garantir apenas uma correta

### 6.3 Como marcar a alternativa correta

A alternativa correta é marcada com um asterisco no final da linha:

```markdown
c) Alternativa correta *
```

O parser converte isso em:

- `data-correta="true"` na alternativa correta
- `data-correct="C"` na lista de alternativas

### 6.4 Como adicionar gabarito e explicação

Use uma linha iniciada por `>`:

```markdown
> A resposta correta é a letra C porque...
```

No HTML gerado:

- o texto vai para `.gabarito`
- a explicação também é copiada para `data-explicacao`
- o bloco aparece apenas depois da interação do usuário

### 6.5 Exemplo funcional completo com 4 alternativas

```markdown
:::questao Qual opção descreve melhor machine learning?
a) Um conjunto de regras fixas que nunca muda
b) Um modo de aprender padrões a partir de dados *
c) Um tipo de cabo de rede
d) Um sistema que só funciona sem computador
> A alternativa correta é a letra B porque machine learning depende do treinamento com dados para encontrar padrões e melhorar previsões.
:::
```

### 6.6 Compatibilidade com o validador atual

O validador atual (`validate_lesson.py`) foi alinhado ao renderer e valida diretamente o Markdown fonte:

- usa regex `^:::questao\s+.+$` para detectar blocos de questão no Markdown
- conta exatamente 2 blocos `:::questao` por aula
- exige exatamente uma alternativa terminando com ` *` em cada bloco

Portanto:

- a sintaxe autoral correta `:::questao` é **compatível** com o validador
- não é necessário gerar HTML manual para passar na validação
- a alternativa correta é marcada apenas com ` *` ao final da linha no Markdown fonte

## 7. Estrutura padrão de uma aula

### 7.1 Template solicitado com frontmatter

Use este modelo como template completo de uma aula ProfessorDash.

O frontmatter YAML é opcional: o validador e o renderer aceitam arquivos com ou sem ele.

```markdown
---
title: Título da aula
description: Descrição curta da aula
order: 1
published: true
---

# Título da aula

Parágrafo introdutório simples apresentando o tema, a relevância e o recorte da aula.

## Abertura

:::objetivo
Defina o que o estudante deve aprender ao final da aula.
:::

:::dica
Antecipe uma estratégia de observação ou estudo.
:::

:::curiosidade
Traga um fato histórico ou contextual curto.
:::

## Desenvolvimento

:::conceito
Apresente a definição central do conteúdo.
:::

Parágrafo de explicação em Markdown comum, sem HTML.

:::importante
Reforce um ponto conceitual que não pode ser confundido.
:::

:::exemplo
Mostre um caso concreto de aplicação.
:::

:::atencao
Corrija um erro comum de interpretação.
:::

:::roteiro
Registre perguntas de condução oral, transições ou exemplos que o professor deve puxar em aula.
:::

## Questões de fixação

:::questao Primeira pergunta de múltipla escolha?
a) Alternativa A
b) Alternativa B *
c) Alternativa C
d) Alternativa D
> Explique por que a alternativa correta é a letra B.
:::

:::questao Segunda pergunta de múltipla escolha?
a) Alternativa A *
b) Alternativa B
c) Alternativa C
d) Alternativa D
> Explique por que a alternativa correta é a letra A.
:::

## Atividade prática

:::exercicio
Oriente uma atividade curta, individual ou em grupo, conectada ao conteúdo.
:::

## Fechamento

:::resumo
- Retome a ideia principal
- Reforce o conceito central
- Relacione com o cotidiano ou com a próxima aula
:::
```

### 7.2 Ordem recomendada dos blocos

Ordem pedagógica sugerida:

1. H1
2. Parágrafo introdutório simples
3. `:::objetivo`
4. `:::dica` ou `:::curiosidade`
5. `:::conceito`
6. `:::importante`
7. `:::exemplo`
8. `:::atencao`
9. `:::roteiro`
10. duas `:::questao`
11. `:::exercicio`
12. `:::resumo`

## 8. Exemplo de aula completa

### 8.1 Observação

O exemplo abaixo foi escrito no formato autoral do renderer do ProfessorDash.

Ele usa:

- Markdown puro
- blocos `:::tipo`
- duas questões interativas no padrão `:::questao`

Este formato é compatível com o renderer e com o validador atual (`validate_lesson.py`).

### 8.2 Aula exemplo

```markdown
# Introdução à Inteligência Artificial

Nesta aula, vamos entender o que é inteligência artificial, onde ela aparece no cotidiano e por que nem toda automação pode ser classificada como IA. O objetivo é construir uma base conceitual clara para reconhecer aplicações reais da área.

## Abertura

:::objetivo
Identificar o que caracteriza uma aplicação de inteligência artificial e distinguir IA de automação simples.
:::

:::curiosidade
O termo inteligência artificial ganhou força em 1956, quando pesquisadores propuseram que máquinas poderiam simular aspectos do raciocínio humano.
:::

:::dica
Ao observar um sistema digital, pergunte sempre: ele usa dados para prever, classificar ou recomendar algo?
:::

## Conceitos iniciais

:::conceito
Inteligência artificial é a área da computação que desenvolve sistemas capazes de executar tarefas como reconhecer padrões, apoiar decisões, classificar informações e fazer previsões.
:::

Quando um sistema aprende a partir de dados anteriores, ele pode melhorar seu desempenho em tarefas específicas sem depender apenas de uma sequência rígida de regras escritas manualmente.

:::importante
Nem todo sistema automatizado é inteligente. Muitos processos digitais apenas executam instruções fixas sem analisar dados.
:::

:::exemplo
Um aplicativo que recomenda vídeos com base no histórico de visualização usa dados do comportamento do usuário para prever novos interesses.
:::

:::atencao
Dizer que “todo computador usa IA” é incorreto. A presença de software não implica aprendizagem, previsão ou reconhecimento de padrões.
:::

:::roteiro
Pergunte aos alunos quais aplicativos “parecem pensar”. Depois, retome cada exemplo e classifique coletivamente se há uso de dados, previsão ou simples regra fixa.
:::

## Questões de fixação

:::questao O que melhor define uma aplicação de inteligência artificial?
a) Um sistema que repete sempre a mesma sequência sem analisar dados
b) Um sistema que usa dados para reconhecer padrões e apoiar decisões *
c) Um dispositivo que precisa estar ligado à internet
d) Um programa com tela colorida e animações
> A alternativa correta é a letra B porque IA envolve análise de dados, reconhecimento de padrões e produção de saídas baseadas nesse processamento.
:::

:::questao Qual situação abaixo representa melhor um uso cotidiano de IA?
a) Um caderno de papel
b) Uma lâmpada comum
c) Um aplicativo que recomenda músicas a partir do histórico do usuário *
d) Uma régua escolar
> A alternativa correta é a letra C porque o sistema usa dados anteriores para estimar preferências e sugerir novos conteúdos.
:::

## Atividade prática

:::exercicio
Em grupos, escolham três ferramentas digitais conhecidas pelos alunos e preencham uma tabela simples com: dados usados, tarefa realizada e motivo pelo qual ela pode ou não ser considerada IA.
:::

## Fechamento

:::resumo
- IA usa dados para reconhecer padrões e apoiar decisões
- automação simples não é necessariamente inteligência artificial
- exemplos cotidianos ajudam a identificar onde a IA realmente aparece
:::
```

## 9. Publicação

### 9.1 Caminho exato dos scripts no workspace atual

- `C:/CODE_TONI/professordash/coimbraclaw/Skills/coimbraclaw-prof/scripts/validate_lesson.py`
- `C:/CODE_TONI/professordash/coimbraclaw/Skills/coimbraclaw-prof/scripts/publish_lesson.py`

### 9.2 Caminho interno de repositório usado pelo script de publicação

No código de `publish_lesson.py`, a constante é:

```python
REPO_PATH = Path("/home/devuser/projects/ProfToniCoimbra")
```

Isso significa:

- o script foi escrito esperando um ambiente onde o repositório didático exista nesse caminho Linux
- a publicação final vai para esse repositório

### 9.3 Argumentos necessários do `publish_lesson.py`

O script exige:

- `--input`
- `--series`
- `--subject`
- `--lesson-number`
- `--title`

Argumento opcional:

- `--push`

Exemplo de chamada:

```bash
python C:/CODE_TONI/professordash/coimbraclaw/Skills/coimbraclaw-prof/scripts/publish_lesson.py \
  --input C:/caminho/temporario/aula.md \
  --series disciplinas-extras \
  --subject inteligencia-artificial \
  --lesson-number 1 \
  --title "Introdução à Inteligência Artificial"
```

### 9.4 O que `validate_lesson.py` verifica de fato

Baseado no código real lido (versão corrigida em 2026-04-05), o validador:

- aceita frontmatter YAML opcional: se presente, é removido antes de validar
- rejeita a tag `<aside>`
- exige que a primeira linha útil seja um H1
- exige um parágrafo simples logo após o H1
- exige as seções `## Questões de fixação`, `## Atividade prática` e `## Fechamento`
- exige exatamente 2 blocos `:::questao` no Markdown fonte (validação direta sobre o texto bruto)
- exige exatamente uma alternativa terminando com ` *` em cada bloco `:::questao`
- gera warning se houver menos de 4 seções H2

### 9.5 O que o `publish_lesson.py` faz de fato

Baseado no código real lido, o script:

1. lê o arquivo informado em `--input`
2. valida o texto lido com `validate_markdown(source_text)`
3. verifica se a combinação `--series` + `--subject` existe em `COURSE_MAP`
4. gera o slug do título
5. monta o nome do arquivo no padrão `aula-XX-slug.md`
6. se a validação falhar, grava uma cópia em `staging/reprovadas/<serie>/<disciplina>/`
7. se a validação passar, grava primeiro em `staging/pendentes/...`
8. copia o mesmo conteúdo para `publicadas/materias/...`
9. remove o arquivo pendente
10. atualiza `manifest.json`
11. executa `git add` no arquivo publicado e no `manifest.json`
12. cria commit se houver alterações
13. opcionalmente tenta `git push -u origin main` quando `--push` é usado
14. imprime um JSON final com o status da operação

### 9.6 Alinhamento do pipeline (corrigido em 2026-04-05)

O estado atual do código é:

- `markdown_extensions.py` converte blocos `:::questao` em HTML interativo
- `validate_lesson.py` valida diretamente o Markdown fonte com regex `:::questao`
- `publish_lesson.py` chama `validate_markdown()` no texto bruto do arquivo

Resultado:

- uma aula escrita no formato autoral correto (`:::questao`) passa na validação
- o pipeline está alinhado ao renderer
- não é necessário gerar HTML manual ou contornar o validador

Conduta correta do agente:

- gerar a aula no formato do renderer com blocos `:::questao`
- chamar o script de publicação normalmente
- se houver reprovação, verificar se as seções obrigatórias estão presentes e se há exatamente 2 questões com uma alternativa marcada com ` *`

## 10. Resposta ao professor

### 10.1 Durante o planejamento

Formato esperado:

```markdown
# Planejamento da sequência

1. Aula 1 - Introdução ao tema
2. Aula 2 - Conceitos centrais
3. Aula 3 - Aplicações práticas
4. Aula 4 - Revisão e atividade

Se aprovar, eu gero a Aula 1 no formato do ProfessorDash.
```

Princípios:

- listar apenas títulos
- manter ordem lógica
- pedir aprovação
- não gerar a aula inteira nessa etapa

### 10.2 Durante a geração

Formato esperado:

- identificar a aula sendo produzida
- informar série e disciplina
- entregar a aula inteira em Markdown
- destacar se há algum bloqueio de validação ou publicação

### 10.3 Após a publicação

Formato esperado:

```markdown
Publicação concluída.

Arquivo: aula-01-introducao-a-inteligencia-artificial.md
Título: Introdução à Inteligência Artificial
Blocos criados: 9
Questões criadas: 2
Validação: ok
Caminho publicado: publicadas/materias/disciplinas-extras/inteligencia-artificial/aula-01-introducao-a-inteligencia-artificial.md
```

Se houver reprovação:

```markdown
Publicação não concluída.

Arquivo gerado: aula-01-introducao-a-inteligencia-artificial.md
Título: Introdução à Inteligência Artificial
Blocos criados: 9
Questões criadas: 2
Validação: reprovada
Motivo: [descrever o erro exato retornado pelo validador]
```

## 11. Regras absolutas

- NUNCA gerar aula completa antes da aprovação do planejamento quando o pedido ainda estiver em fase de definição.
- NUNCA publicar em série ou disciplina fora da tabela de `repo-layout.md`.
- NUNCA usar HTML bruto como forma principal de autoria da aula.
- NUNCA começar a aula com bloco especial, lista, tabela ou citação; a primeira linha útil deve ser H1 e a linha seguinte deve ser um parágrafo simples.
- NUNCA omitir as seções `## Questões de fixação`, `## Atividade prática` e `## Fechamento` quando o objetivo for seguir o validador atual.
- NUNCA marcar mais de uma alternativa correta em um mesmo bloco `:::questao`.
- NUNCA esconder incompatibilidades do pipeline para “forçar” publicação.
- NUNCA afirmar que `:::roteiro` fica oculto no modo aluno sem qualificar isso; o template lido comprova exclusão dos slides, não ocultação geral por modo aluno.
- NUNCA gerar HTML manual para "satisfazer" o validador; o validador valida o Markdown fonte com `:::questao`, não HTML renderizado.
- SEMPRE incluir frontmatter YAML se o professor solicitar metadados; o validador aceita frontmatter opcional (remove antes de validar).
- SEMPRE usar Markdown limpo com blocos `:::tipo` para autoria de componentes especiais.
- SEMPRE revisar o comportamento real de `core/markdown_extensions.py` quando houver dúvida sobre sintaxe de bloco.
- SEMPRE revisar `templates/aulas/aula_detalhe.html` quando houver dúvida sobre aparência visual final.
- SEMPRE conferir `validate_lesson.py` antes de prometer publicação automática.
- SEMPRE deixar explícito quando houver divergência entre renderer, filtro `markdownify` e pipeline de publicação.
- SEMPRE gerar uma aula por vez após a aprovação.
- SEMPRE usar nomes de arquivo no padrão `aula-XX-titulo-slug.md`.
- SEMPRE informar ao professor o nome do arquivo, o título, o número de blocos e a quantidade de questões ao final do processo.
- SEMPRE priorizar o formato nativo do ProfessorDash na autoria da aula.
- SEMPRE tratar o código do repositório como fonte de verdade acima de documentação antiga, notas resumidas ou memória operacional.

## Apêndice A. Mapa real dos callouts

Mapa extraído de `CALLOUT_MAP` em `core/markdown_extensions.py`.

| Bloco | Ícone | Título padrão | Classe CSS |
|---|---|---|---|
| `objetivo` | `🎯` | `Objetivo` | `c-green` |
| `importante` | `⚠️` | `Importante` | `c-amber` |
| `dica` | `💡` | `Dica` | `c-blue` |
| `exemplo` | `📝` | `Exemplo` | `c-violet` |
| `atencao` | `🚨` | `Atencao` | `c-coral` |
| `conceito` | `📖` | `Conceito` | `c-blue` |
| `exercicio` | `✍️` | `Exercicio` | `c-violet` |
| `curiosidade` | `🔍` | `Curiosidade` | `c-blue` |

## Apêndice B. Resumo das inconsistências corrigidas nesta skill

1. Frontmatter

- a documentação anterior afirmava que o validador rejeita frontmatter YAML
- o validador foi corrigido em 2026-04-05: frontmatter é opcional e removido antes de validar
- tanto o renderer (`|markdownify`) quanto o validador aceitam frontmatter; ambos o stripam antes de processar o conteúdo
- esta skill documenta o estado corrigido: frontmatter YAML pode ser incluído ou omitido sem impacto na validação

2. Questões interativas

- a skill anterior documentava um conflito: o renderer gerava `data-idx="q-1"` mas o validador buscava `data-idx="q1"` no HTML
- o validador foi corrigido em 2026-04-05 e passou a validar o Markdown fonte diretamente via `:::questao`
- esta skill documenta o estado corrigido: `:::questao` é o formato autoral correto e é aceito pelo validador atual

3. Roteiro

- a skill anterior afirmava que `:::roteiro` fica oculto no modo aluno
- no template lido, o que se comprova é exclusão dos slides de apresentação
- esta skill corrige a descrição para o que o arquivo realmente mostra

4. Publicação

- a skill anterior documentava que o pipeline estava desalinhado (validador vs. renderer)
- o validador foi corrigido em 2026-04-05: `validate_lesson.py` agora valida `:::questao` diretamente no Markdown
- o pipeline está alinhado: aulas escritas no formato autoral correto passam na validação e podem ser publicadas normalmente

5. Fonte de verdade

- a skill anterior resumia o comportamento
- esta skill documenta o comportamento real do renderer, do CSS e dos scripts a partir do código lido
