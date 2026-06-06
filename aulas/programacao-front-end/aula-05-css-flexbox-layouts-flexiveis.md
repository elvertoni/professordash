# Aula 05 — CSS Flexbox: Layouts flexíveis

Já pensou em criar um layout que se adapta automaticamente ao tamanho da tela, sem precisar calcular porcentagens ou usar floats complicados? O Flexbox é um modelo de layout do CSS que foi criado exatamente para isso: distribuir espaços e alinhar itens em uma dimensão (linha ou coluna) de forma previsível e inteligente. Nesta aula prática, você vai construir um cardápio digital responsivo usando apenas Flexbox.

## O que vamos construir

Um cardápio digital com três colunas de pratos que se reorganizam sozinhas quando a tela diminui — os cards encolhem, quebram para a linha de baixo e o layout todo fica bonito em qualquer tamanho de tela.

:::objetivo Resultado final
Uma página de cardápio com no mínimo 6 cards de pratos, organizados
em linhas flexíveis. Ao redimensionar o navegador, os cards devem
se ajustar automaticamente sem usar media queries.
:::

## Pré-requisitos

:::dica Para esta aula você precisa de
Editor de código, navegador moderno, arquivo index.html com a
estrutura da página criada e um arquivo style.css ligado a ele.
Conhecimento básico de seletores CSS.
:::

## Passo a passo

1. **Criar a estrutura HTML do cardápio** — Cada prato será um card dentro de um container flexível.

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cardápio</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <h1>Cardápio Digital</h1>
    </header>
    <main class="cardapio">
        <div class="card">
            <h2>Hambúrguer</h2>
            <p class="preco">R$ 24,90</p>
            <p>Pão artesanal, hambúrguer 180g, queijo cheddar</p>
        </div>
        <div class="card">
            <h2>Pizza Margherita</h2>
            <p class="preco">R$ 39,90</p>
            <p>Molho de tomate, mussarela, manjericão</p>
        </div>
        <div class="card">
            <h2>Salada Caesar</h2>
            <p class="preco">R$ 19,90</p>
            <p>Alface romana, croutons, parmesão, molho Caesar</p>
        </div>
    </main>
</body>
</html>
```

2. **Aplicar display flex no container** — No CSS, transforme `.cardapio` em um container flex.

```css
.cardapio {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: center;
    padding: 20px;
}
```

A propriedade `display: flex` ativa o Flexbox no container. `flex-wrap: wrap` permite que os cards quebrem para a linha seguinte quando não couberem mais.

3. **Estilizar os cards** — Defina largura, padding e aparência de cada card.

```css
.card {
    background-color: #f9f9f9;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
    width: 280px;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}

.card:hover {
    transform: scale(1.02);
}

.preco {
    font-size: 1.5rem;
    font-weight: bold;
    color: #2a9d8f;
}
```

4. **Explorar flex-direction** — Experimente mudar a direção dos itens com `flex-direction`.

```css
/* Coluna (padrão é row) */
.cardapio {
    flex-direction: column;
    align-items: center;
}

/* Ou volte para linha */
.cardapio {
    flex-direction: row;
    flex-wrap: wrap;
}
```

5. **Controlar alinhamento com align-items e justify-content** — Brinque com as propriedades de alinhamento.

```css
.cardapio {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-around; /* espaço igual ao redor */
    align-items: stretch;          /* todos com mesma altura */
    gap: 20px;
}
```

`justify-content` alinha no eixo principal (horizontal em row) e `align-items` no eixo transversal (vertical em row). `stretch` faz todos os cards terem a mesma altura.

## Checkpoint

:::objetivo Você está no caminho certo se
A página exibe os cards lado a lado em telas grandes e eles quebram
para a linha de baixo ao encolher a janela. Todos os cards têm a
mesma altura (por causa do stretch) e há espaçamento consistente
entre eles.
:::

## Erros comuns

:::atencao Sintoma: os cards não ficam lado a lado
Causa: esqueceu de aplicar display: flex no container pai.
Correção: adicione display: flex à classe .cardapio, não aos
cards individuais. O Flexbox só funciona do pai para os filhos.
:::

:::atencao Sintoma: os cards ficam todos amontoados sem espaçamento
Causa: não usou gap ou margin nos itens.
Correção: use gap: 20px no container flex. Diferente de margin,
o gap não acumula nas bordas externas do container.
:::

## Desafio

Adicione 3 cards a mais ao cardápio (total 6) e use `flex: 0 1 300px` nos cards individuais para controlar o crescimento e encolhimento de cada um.

:::importante Desafio extra
Para quem terminar primeiro: adicione uma classe .destaque no
segundo card e use a propriedade order do Flexbox para fazer
esse card aparecer primeiro, mesmo estando no meio do HTML.
:::

## Código completo

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cardápio Digital</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f4f4f4; }
        header {
            background: #2a9d8f;
            color: white;
            text-align: center;
            padding: 30px;
        }
        .cardapio {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
            padding: 40px 20px;
        }
        .card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            width: 280px;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
            flex: 0 1 280px;
        }
        .card:hover { transform: scale(1.02); }
        .card h2 { margin-bottom: 10px; color: #264653; }
        .preco {
            font-size: 1.5rem;
            font-weight: bold;
            color: #2a9d8f;
            margin-bottom: 8px;
        }
    </style>
</head>
<body>
    <header>
        <h1>Cardápio Digital</h1>
    </header>
    <main class="cardapio">
        <div class="card">
            <h2>Hambúrguer</h2>
            <p class="preco">R$ 24,90</p>
            <p>Pão artesanal, hambúrguer 180g, queijo cheddar</p>
        </div>
        <div class="card destaque">
            <h2>Pizza Margherita</h2>
            <p class="preco">R$ 39,90</p>
            <p>Molho de tomate, mussarela, manjericão</p>
        </div>
        <div class="card">
            <h2>Salada Caesar</h2>
            <p class="preco">R$ 19,90</p>
            <p>Alface romana, croutons, parmesão, molho Caesar</p>
        </div>
        <div class="card">
            <h2>Petit Gateau</h2>
            <p class="preco">R$ 16,90</p>
            <p>Bolo de chocolate com centro derretido e sorvete</p>
        </div>
        <div class="card">
            <h2>Suco Natural</h2>
            <p class="preco">R$ 9,90</p>
            <p>Laranja, limão, abacaxi ou morango</p>
        </div>
        <div class="card">
            <h2>Porção de Batata</h2>
            <p class="preco">R$ 14,90</p>
            <p>Batata frita crocante com molho especial</p>
        </div>
    </main>
</body>
</html>
```

## Fechamento

:::resumo
- Flexbox organiza itens em uma dimensão (linha ou coluna)
- display: flex ativa o Flexbox no container pai
- flex-wrap: wrap permite quebra de linha automática
- justify-content e align-items controlam o alinhamento
- gap cria espaçamento consistente entre itens
- Próxima aula: CSS Grid — layouts bidimensionais para projetos ainda mais complexos
:::
