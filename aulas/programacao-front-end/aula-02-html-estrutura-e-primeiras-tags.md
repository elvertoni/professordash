# Aula 02 — HTML: Estrutura e primeiras tags

Toda página web que você visita começa com HTML. É a linguagem que dá
estrutura ao conteúdo — como o esqueleto de um corpo. Nesta aula prática,
você vai criar sua primeira página HTML do zero, aprender as tags
fundamentais e entender como a estrutura básica de um documento funciona.
Ao final, você terá um arquivo HTML próprio que pode abrir em qualquer
navegador.

## O que vamos construir

Uma página pessoal simples com título, subtítulo, parágrafo de apresentação e uma lista de hobbies. Tudo funcionando em um único arquivo `.html`.

:::objetivo Resultado final
Uma página HTML que abre no navegador exibindo: um título principal,
uma saudação em heading menor, um parágrafo sobre você e duas listas
(uma ordenada e uma não-ordenada).
:::

## Pré-requisitos

:::dica Para esta aula você precisa de
Editor de texto (VS Code, Sublime ou até Bloco de Notas), navegador
moderno (Chrome, Firefox ou Edge) e uma pasta de trabalho chamada
`meu-site` no seu computador.
:::

## Passo a passo

1. **Criar a estrutura básica do HTML** — Todo documento HTML começa com `` que informa ao navegador que estamos usando HTML5.

```html



    
    
    Minha Página




```

2. **Adicionar o cabeçalho da página** — Dentro de ``, use `` para o título principal e `` para um subtítulo.

```html
Olá, eu sou [Seu Nome]
Estudante de Desenvolvimento Web
```

3. **Inserir um parágrafo de apresentação** — A tag `` cria parágrafos. Escreva de 2 a 3 linhas sobre você.

```html
Estou aprendendo HTML no curso técnico da SEED-PR. Esta é minha
primeira página criada do zero. Gosto de tecnologia e quero me tornar
desenvolvedor web.
```

4. **Criar uma lista não-ordenada** — Use `` (unordered list) com itens `` para listar seus hobbies.

```html
Meus hobbies

    Jogar videogame
    Ouvir música
    Programar

```

5. **Criar uma lista ordenada** — Use `` (ordered list) para listar suas metas de aprendizado.

```html
Metas de aprendizado

    Aprender HTML e CSS
    Dominar JavaScript
    Criar meu próprio site

```

## Checkpoint

:::objetivo Você está no caminho certo se
Ao abrir o arquivo `.html` no navegador, você vê: um título grande,
um subtítulo menor, um parágrafo, uma lista com marcadores (hobbies)
e uma lista numerada (metas). O título da aba do navegador mostra
"Minha Página".
:::

## Erros comuns

:::atencao Sintoma: a página aparece em branco
Causa: o conteudo esta fora das tags body ou o arquivo foi salvo
com extensao .txt em vez de .html. Correcao: verifique se todo
o conteudo visivel esta entre body e /body, e salve como index.html.
:::

:::atencao Sintoma: as tags aparecem escritas na tela
Causa: voce usou os simbolos de menor e maior como texto comum ou
esqueceu de fechar a tag. O navegador interpreta cada abertura de
tag como inicio de elemento. Correcao: garanta que tags tem a sintaxe
exata .
:::

## Desafio

Adicione uma imagem à sua página usando a tag `` com um atributo `src` apontando para uma imagem da internet (ex.: `https://placehold.co/200`).

:::importante Desafio extra
Para quem terminar primeiro: pesquise sobre a tag a e adicione
um link para o site da sua escola ou do ProfessorDash
em https://aulas.tonicoimbra.com.
:::

## Código completo

```html



    
    
    Minha Página


    Olá, eu sou [Seu Nome]
    Estudante de Desenvolvimento Web
    Estou aprendendo HTML no curso tecnico da SEED-PR. Esta e minha
    primeira pagina criada do zero. Gosto de tecnologia e quero me tornar
    desenvolvedor web.
    Meus hobbies
    
        Jogar videogame
        Ouvir musica
        Programar
    
    Metas de aprendizado
    
        Aprender HTML e CSS
        Dominar JavaScript
        Criar meu proprio site
    
    
    

    Visite o ProfessorDash


```

## Fechamento

:::resumo
- HTML usa tags para marcar o significado do conteudo
- Tags h1 a h6 sao headings em ordem de importancia
- p cria paragrafos, ul e ol criam listas
- A tag a cria hyperlinks; img exibe imagens
- Proxima aula: HTML semantico e por que ele importa para acessibilidade
:::
