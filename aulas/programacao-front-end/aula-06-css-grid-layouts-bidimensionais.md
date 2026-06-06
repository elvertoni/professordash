# Aula 06 — CSS Grid: Layouts bidimensionais

O Flexbox resolve o problema de distribuir itens em uma linha ou coluna. Mas e quando você precisa controlar linhas e colunas ao mesmo tempo — como um mural de fotos, um dashboard ou a página inicial de um site de notícias? O CSS Grid foi criado para isso: layouts bidimensionais onde você define a grade e posiciona os elementos onde quiser. Nesta aula, você vai construir a página inicial de um portal de notícias usando Grid.

## O que vamos construir

A página inicial de um portal de notícias com header, sidebar, área de destaque, grid de artigos e footer — tudo organizado com CSS Grid em áreas nomeadas.

:::objetivo Resultado final
Um layout de portal com 6 áreas visuais (header, nav, destaque,
artigos, sidebar, footer) organizadas em uma grade 3x4 que se
reorganiza em telas menores.
:::

## Pré-requisitos

:::dica Para esta aula você precisa de
Editor de código, navegador moderno e um arquivo HTML+CSS em branco.
Conforto com seletores CSS e flexbox (para combinarmos técnicas).
:::

## Passo a passo

1. **Criar a estrutura HTML do portal** — Cada seção será um elemento filho direto do container grid.

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal de Notícias</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="cabecalho">Header do Portal</header>
    <nav class="nav">Navegação</nav>
    <section class="destaque">Notícia em Destaque</section>
    <main class="artigos">Grade de Artigos</main>
    <aside class="sidebar">Sidebar</aside>
    <footer class="footer">Rodapé</footer>
</body>
</html>
```

2. **Aplicar display: grid e definir template areas** — No CSS, crie a grade 3 colunas x 4 linhas com áreas nomeadas.

```css
body {
    display: grid;
    grid-template-areas:
        "header   header   header"
        "nav      destaque sidebar"
        "nav      artigos  sidebar"
        "footer   footer   footer";
    grid-template-columns: 200px 1fr 250px;
    grid-template-rows: auto 1fr 2fr auto;
    min-height: 100vh;
    gap: 8px;
    margin: 0;
}
```

`grid-template-areas` define visualmente onde cada área fica. Cada linha entre aspas representa uma linha da grade, e cada palavra uma coluna. O ponto `.` seria usado para célula vazia.

3. **Posicionar cada elemento com grid-area** — Cada filho recebe o nome correspondente.

```css
.cabecalho { grid-area: header; }
.nav       { grid-area: nav; }
.destaque  { grid-area: destaque; }
.artigos   { grid-area: artigos; }
.sidebar   { grid-area: sidebar; }
.footer    { grid-area: footer; }

/* Estilização básica para enxergar as áreas */
.cabecalho { background: #1a1a2e; color: white; padding: 20px; }
.nav       { background: #16213e; color: white; padding: 20px; }
.destaque  { background: #0f3460; color: white; padding: 20px; }
.artigos   { background: #e8e8e8; padding: 20px; }
.sidebar   { background: #533483; color: white; padding: 20px; }
.footer    { background: #1a1a2e; color: white; padding: 20px; }
```

4. **Criar um sub-grid de artigos** — Dentro da área de artigos, use Flexbox ou Grid para os cards.

```css
.artigos {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
}

.card {
    background: white;
    border-radius: 6px;
    padding: 16px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
```

A função `repeat(auto-fill, minmax(200px, 1fr))` cria colunas responsivas que se ajustam automaticamente ao espaço disponível.

5. **Deixar responsivo com media query** — Em telas pequenas, empilhe tudo em uma coluna.

```css
@media (max-width: 768px) {
    body {
        grid-template-areas:
            "header"
            "nav"
            "destaque"
            "artigos"
            "sidebar"
            "footer";
        grid-template-columns: 1fr;
    }
}
```

## Checkpoint

:::objetivo Você está no caminho certo se
A página exibe 6 áreas coloridas na disposição correta: header no
topo ocupando toda a largura, nav à esquerda, sidebar à direita,
destaque e artigos no centro, footer embaixo. Ao redimensionar para
menos de 768px, tudo vira uma coluna única.
:::

## Erros comuns

:::atencao Sintoma: grid-area não funciona e o conteúdo fica empilhado
Causa: os nomes no grid-template-areas e no grid-area não batem, ou
há espaço extra nas aspas. O CSS é sensível a espaços em branco nas
strings de areas. Verifique se cada nome aparece exatamente igual.
:::

:::atencao Sintoma: a grade cria linhas extras não planejadas
Causa: algum elemento filho direto do body não tem grid-area definido
e está sendo automaticamente posicionado na grade.
Correção: todo filho direto de um container grid precisa ter grid-area
ou ser explicitamente posicionado com grid-column/grid-row.
:::

## Desafio

Adicione uma barra de busca no header usando flexbox e preencha a sidebar com uma lista de categorias (Tecnologia, Esportes, Cultura, Economia) com links estilizados.

:::importante Desafio extra
Para quem terminar primeiro: crie uma variante do layout que troca
a sidebar de lado (direita para esquerda) usando apenas a propriedade
order do Grid ou alterando o grid-template-areas.
:::

## Código completo

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal de Notícias</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            display: grid;
            grid-template-areas:
                "header  header  header"
                "nav     destaque sidebar"
                "nav     artigos  sidebar"
                "footer  footer  footer";
            grid-template-columns: 200px 1fr 250px;
            grid-template-rows: auto 1fr 2fr auto;
            min-height: 100vh;
            gap: 8px;
            padding: 8px;
            background: #f0f0f0;
        }
        .cabecalho { grid-area: header; background: #1a1a2e; color: white; padding: 24px; border-radius: 6px; }
        .nav       { grid-area: nav; background: #16213e; color: white; padding: 20px; border-radius: 6px; }
        .destaque  { grid-area: destaque; background: #0f3460; color: white; padding: 20px; border-radius: 6px; }
        .artigos   { grid-area: artigos; display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }
        .sidebar   { grid-area: sidebar; background: #533483; color: white; padding: 20px; border-radius: 6px; }
        .footer    { grid-area: footer; background: #1a1a2e; color: white; padding: 16px; text-align: center; border-radius: 6px; }
        .card {
            background: white;
            border-radius: 6px;
            padding: 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            color: #333;
        }
        .card h3 { margin-bottom: 8px; font-size: 1rem; }
        @media (max-width: 768px) {
            body {
                grid-template-areas:
                    "header"
                    "nav"
                    "destaque"
                    "artigos"
                    "sidebar"
                    "footer";
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header class="cabecalho"><h1>Portal de Notícias</h1></header>
    <nav class="nav"><p>Links de navegação</p></nav>
    <section class="destaque"><h2>Notícia em Destaque</h2><p>Resumo da principal notícia do dia.</p></section>
    <main class="artigos">
        <div class="card"><h3>Artigo 1</h3><p>Resumo do artigo...</p></div>
        <div class="card"><h3>Artigo 2</h3><p>Resumo do artigo...</p></div>
        <div class="card"><h3>Artigo 3</h3><p>Resumo do artigo...</p></div>
        <div class="card"><h3>Artigo 4</h3><p>Resumo do artigo...</p></div>
    </main>
    <aside class="sidebar"><p>Conteúdo complementar, anúncios, links.</p></aside>
    <footer class="footer"><p>&copy; 2026 Portal de Notícias</p></footer>
</body>
</html>
```

## Fechamento

:::resumo
- CSS Grid trabalha com duas dimensões simultaneamente (linhas e colunas)
- grid-template-areas cria um mapa visual do layout
- grid-area posiciona cada elemento no mapa
- repeat(auto-fill, minmax(...)) cria colunas responsivas sem media queries
- Grid e Flexbox se complementam — use Grid para o macro layout e Flexbox para componentes internos
- Próxima aula: JavaScript — variáveis, tipos e operadores
:::
