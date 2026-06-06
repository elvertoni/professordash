# Aula 07 — HTML Semântico: dando significado à estrutura

Você já sabe que HTML é a linguagem de marcação que estrutura páginas web. Mas será que existe uma forma "certa" de escrever HTML? Até agora você provavelmente usou `<div>` para tudo — e funciona. Porém, desde 2014 (HTML5), a web ganhou tags que carregam significado, não apenas forma. Usar essas tags é o que chamamos de **HTML Semântico**: escrever código que descreve o conteúdo, não apenas a aparência. Nesta aula, você vai aprender por que isso importa e como aplicar na prática.

## O problema das `<div>` genéricas

Quando uma página é construída inteiramente com `<div>` e `<span>`, o navegador e os mecanismos de busca enxergam apenas uma lista plana de blocos genéricos. Não há distinção entre cabeçalho, navegação, conteúdo principal ou rodapé — tudo é "div". Isso dificulta acessibilidade, indexação e manutenção.

:::importante HTML Semântico vs HTML Não-Semântico
O HTML não-semântico usa tags genéricas como `<div>` e `<span>` para
tudo. O HTML semântico usa tags específicas como `<header>`, `<nav>`,
`<main>`, `<article>` e `<footer>` que descrevem o propósito de cada
parte da página.
:::

O resultado de ignorar semântica? Leitores de tela não conseguem pular para o conteúdo principal, Google não identifica a hierarquia da página, e outro desenvolvedor leva o dobro do tempo para entender seu código.

## Tags semânticas: o vocabulário da estrutura

O HTML5 introduziu um conjunto de tags que substituem a `<div>` genérica em contextos específicos. Cada uma tem um significado claro e um comportamento esperado.

:::conceito Tags estruturais do HTML5
| Tag | Propósito | Substitui |
|-----|-----------|-----------|
| `<header>` | Cabeçalho da página ou seção | `<div class="header">` |
| `<nav>` | Navegação principal | `<div class="nav">` |
| `<main>` | Conteúdo principal (único por página) | `<div class="main">` |
| `<article>` | Conteúdo independente (post, notícia) | `<div class="post">` |
| `<section>` | Agrupamento temático | `<div class="section">` |
| `<aside>` | Conteúdo complementar (sidebar) | `<div class="sidebar">` |
| `<footer>` | Rodapé da página ou seção | `<div class="footer">` |
:::

Note que essas tags não mudam a aparência da página por si só — elas são elementos de bloco como `<div>`. A diferença está no **significado** que carregam para navegadores, leitores de tela e mecanismos de busca.

## Exemplo prático: comparando os dois mundos

Veja como a mesma página fica com e sem HTML semântico.

:::exemplo Página sem semântica (apenas divs)
```html
<div class="cabecalho">
  <div class="logo">Meu Site</div>
  <div class="menu">
    <a href="/">Início</a>
    <a href="/sobre">Sobre</a>
  </div>
</div>
<div class="conteudo">
  <div class="artigo">
    <h1>Título do Post</h1>
    <p>Conteúdo interessante aqui.</p>
  </div>
</div>
<div class="rodape">
  <p>&copy; 2026</p>
</div>
```
:::

:::exemplo Página com semântica HTML5
```html
<header>
  <h1>Meu Site</h1>
  <nav>
    <a href="/">Início</a>
    <a href="/sobre">Sobre</a>
  </nav>
</header>
<main>
  <article>
    <h1>Título do Post</h1>
    <p>Conteúdo interessante aqui.</p>
  </article>
</main>
<footer>
  <p>&copy; 2026</p>
</footer>
```
:::

A diferença é sutil no código, mas enorme no significado. Um leitor de tela pode pular diretamente para `<main>` ignorando a navegação. O Google prioriza o `<article>` como conteúdo principal. E você, desenvolvedor, entende a estrutura só de olhar as tags.

:::curiosidade Origem do HTML semântico
O termo "Web Semântica" foi cunhado por Tim Berners-Lee em 2001,
mas o HTML semântico como conhecemos só chegou com o HTML5 em 2014.
A ideia original era que máquinas pudessem "entender" o conteúdo
tanto quanto humanos. Embora a Web Semântica plena não tenha se
concretizado, o HTML semântico tornou-se padrão essencial.
:::

## Regras de ouro da semântica

Usar tags semânticas não é complicado, mas exige disciplina. Algumas regras ajudam a evitar erros comuns.

:::importante Regras práticas
1. Use `<main>` **uma única vez** por página — ele envolve o conteúdo
   principal exclusivo.
2. `<header>` e `<footer>` podem aparecer várias vezes: um por página
   e um dentro de cada `<article>` ou `<section>`.
3. `<nav>` é para navegação **principal**, não para qualquer grupo de
   links. Um menu de redes sociais no rodapé não precisa de `<nav>`.
4. `<article>` funciona sozinho: se você pudesse pegar aquela seção
   e colocar em outra página fazendo sentido, é um article.
5. `<section>` precisa de um título (`<h1>`-`<h6>`) — semanticamente
   toda seção tem um assunto.
:::

## Questões de fixação

:::questao Qual tag HTML5 deve ser usada para envolver o conteúdo principal e exclusivo de uma página?
a) `<section>`
b) `<article>`
c) `<main>` *
d) `<div id="content">`
> A resposta correta é `<main>`. Ela representa o conteúdo principal da página e deve aparecer apenas uma vez. `<section>` agrupa conteúdo temático, `<article>` é para conteúdo independente, e `<div>` não carrega significado semântico.
:::

:::questao Em qual situação NÃO é semanticamente correto usar a tag `<nav>`?
a) Menu principal de navegação do site
b) Links de redes sociais no rodapé *
c) Índice de páginas de um manual
d) Breadcrumb (migalhas de pão)
> A tag `<nav>` é reservada para blocos de navegação principal. Links de redes sociais no rodapé não constituem navegação principal do site — são links complementares e devem ficar em `<footer>` sem `<nav>`. Breadcrumbs, por outro lado, são um padrão clássico de navegação e `<nav>` é apropriado.
:::

## Atividade prática — refatorando um site de notícias

Você recebeu um HTML de um site de notícias que usa apenas `<div>`. Seu trabalho é refatorá-lo aplicando HTML semântico.

```html
<div class="pagina">
  <div class="topo">
    <h1>Notícias da Cidade</h1>
    <div class="menu">
      <a href="/">Home</a>
      <a href="/politica">Política</a>
      <a href="/esportes">Esportes</a>
    </div>
  </div>
  <div class="conteudo">
    <div class="materia">
      <h2>Chuva forte atinge a região</h2>
      <p>A cidade de Curitiba registrou o maior volume de chuva dos últimos 10 anos...</p>
    </div>
    <div class="lateral">
      <h3>Últimas</h3>
      <ul>
        <li>Trânsito lento na BR-277</li>
        <li>Previsão do tempo para amanhã</li>
      </ul>
    </div>
  </div>
  <div class="rodape">
    <p>Notícias da Cidade &copy; 2026</p>
  </div>
</div>
```

:::objetivo Entrega
Entregue o HTML refatorado com tags semânticas (`<header>`, `<nav>`,
`<main>`, `<article>`, `<aside>`, `<footer>`). Salve como
`noticias-semantico.html`. Dica: o "conteudo" vira `<main>`, a
"materia" vira `<article>`, e o "lateral" vira `<aside>`.
:::

:::roteiro
Pessoal, vou passar de carteira em carteira ver como está a
refatoração. Lembrem-se: não precisa mudar o CSS — as tags semânticas
são elementos de bloco, iguais à div. A diferença é invisível no
visual mas essencial na semântica.
:::

## Fechamento

:::resumo
- HTML Semântico usa tags que descrevem o PROPÓSITO do conteúdo
- Tags como `<header>`, `<nav>`, `<main>`, `<article>`, `<aside>` e
  `<footer>` substituem `<div>` genéricas em contextos específicos
- Benefícios: acessibilidade, SEO, manutenibilidade do código
- `<main>` deve ser único por página; `<header>`/`<footer>` podem se
  repetir dentro de articles/sections
- Próxima aula: introdução ao CSS Flexbox para layouts responsivos
:::
