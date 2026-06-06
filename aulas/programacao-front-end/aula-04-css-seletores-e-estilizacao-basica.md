# Aula 04 — CSS: Seletores e estilização básica

Você já sabe estruturar uma página com HTML. Mas uma página sem CSS é como
um caderno sem capa — funcional, mas sem identidade visual. CSS (Cascading
Style Sheets) é a linguagem que dá cor, espaçamento, fontes e layout às
páginas web. Nesta aula prática, você vai aprender a conectar CSS ao HTML
e usar seletores para estilizar elementos específicos.

## O que vamos construir

Vamos pegar a página HTML da aula anterior e aplicar estilos: cores personalizadas, fontes diferentes, margens e espaçamentos, e um fundo estilizado.

:::objetivo Resultado final
Uma pagina HTML estilizada com: fundo de cor suave, titulo em azul
escuro, fonte diferente da padrao, margens laterais e uma borda ao
redor da lista de hobbies.
:::

## Pré-requisitos

:::dica Para esta aula voce precisa de
O arquivo index.html da aula anterior (ou crie um novo), editor de
texto e navegador para testar. Crie um arquivo estilo.css na mesma
pasta.
:::

## Passo a passo

1. **Criar o arquivo CSS e conectar ao HTML** — No `<head>` do HTML, adicione a tag `<link>` que aponta para seu CSS.

```html
<link rel="stylesheet" href="estilo.css">
```

2. **Seletores de tag** — O seletor mais básico: o nome da tag. Todas as tags daquele tipo recebem o estilo.

```css
body {
    background-color: #f0f4f8;
    font-family: 'Segoe UI', Tahoma, sans-serif;
    margin: 40px;
}
h1 {
    color: #1a365d;
    text-align: center;
    font-size: 32px;
}
h2 {
    color: #2b6cb0;
}
```

3. **Seletores de classe** — Classes são reutilizáveis e começam com ponto (`.`) no CSS. No HTML, use `class="nome"`.

```css
.destaque {
    background-color: #e2e8f0;
    padding: 15px;
    border-radius: 8px;
}
```

4. **Seletores de ID** — IDs são únicos por página e usam `#` no CSS. Use com moderação.

```css
#titulo-principal {
    border-bottom: 3px solid #2b6cb0;
    padding-bottom: 10px;
}
```

5. **Estilizar listas com borda e espaçamento** — Combine seletores para um visual mais caprichado.

```css
ul, ol {
    background-color: white;
    border: 1px solid #cbd5e0;
    border-radius: 6px;
    padding: 20px 40px;
    max-width: 400px;
}
li {
    margin-bottom: 8px;
}
```

## Checkpoint

:::objetivo Voce esta no caminho certo se
A pagina tem fundo acinzentado claro (#f0f4f8), o titulo principal
e azul escuro e centralizado, os paragrafos tem fonte sem serifa, e
as listas aparecem dentro de uma caixa branca com borda arredondada.
:::

## Erros comuns

:::atencao Sintoma: o CSS nao aparece na pagina
Causa: o caminho do href no link esta errado ou o arquivo CSS tem
extensao .txt em vez de .css. Correcao: verifique se estilo.css
esta na mesma pasta do HTML e se a tag link esta dentro de head.
:::

:::atencao Sintoma: o estilo funciona em um elemento mas nao em outro
Causa: conflito de especificidade ou erro de digitacao no nome da
classe ou ID. Correcao: use o DevTools (F12) para inspecionar o
elemento e ver quais estilos estao sendo aplicados.
:::

## Desafio

Adicione uma classe `.card` que crie um cartão estilizado (fundo branco, sombra suave com `box-shadow`, padding e borda arredondada). Aplique essa classe a um ou mais elementos da página.

:::importante Desafio extra
Pesquise sobre a propriedade transition no CSS e faca os cartoes
mudarem de cor suavemente quando o mouse passa por cima (hover).
:::

## Código completo

```css
body {
    background-color: #f0f4f8;
    font-family: 'Segoe UI', Tahoma, sans-serif;
    margin: 40px;
    color: #2d3748;
}
#titulo-principal {
    color: #1a365d;
    text-align: center;
    font-size: 32px;
    border-bottom: 3px solid #2b6cb0;
    padding-bottom: 10px;
}
h2 {
    color: #2b6cb0;
    margin-top: 30px;
}
.destaque {
    background-color: #e2e8f0;
    padding: 15px;
    border-radius: 8px;
    font-size: 18px;
}
ul, ol {
    background-color: white;
    border: 1px solid #cbd5e0;
    border-radius: 6px;
    padding: 20px 40px;
    max-width: 400px;
}
li {
    margin-bottom: 8px;
    line-height: 1.6;
}
.card {
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin: 20px 0;
}
```

## Fechamento

:::resumo
- CSS e conectado ao HTML via link rel stylesheet
- Seletores de tag, classe (.) e ID (#) tem niveis diferentes de
  especificidade
- Classes sao reutilizaveis; IDs devem ser unicos
- Propriedades comuns: color, background-color, font-family, margin,
  padding, border, border-radius
- Proxima aula: layouts flexiveis com Flexbox
:::
