# Aula 12 — Projeto final: Mini e-commerce front-end

Chegou o momento de juntar tudo que você aprendeu nas 11 aulas anteriores em um único projeto completo. Você vai construir um mini e-commerce com HTML semântico, CSS Flexbox/Grid, JavaScript para interatividade e localStorage para persistência. O projeto é um carrinho de compras funcional: você exibe produtos, adiciona ao carrinho, ajusta quantidades e vê o total.

## O que vamos construir

Uma loja virtual com catálogo de produtos, carrinho de compras lateral e funcionalidades completas de e-commerce. Ao final, você terá uma aplicação front-end completa e funcional, sem nenhuma dependência externa.

:::objetivo Resultado final
Página de loja funcional com: grid de produtos com imagens e
preços, carrinho lateral com itens adicionados, contador no
ícone do carrinho, ajuste de quantidade por item, cálculo de
total e persistência dos itens no localStorage.
:::

## Pré-requisitos

:::dica Para esta aula você precisa de
Todo o conteúdo das aulas 01 a 11. Editor de código, navegador
moderno. Vontade de construir algo do zero — este projeto é seu
portfólio.
:::

## Passo a passo

1. **Criar a estrutura HTML semântica** — Use header, main, section, aside.

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minha Loja</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <h1>Minha Loja</h1>
        <button id="btnCarrinho">🛒 Carrinho (<span id="contador">0</span>)</button>
    </header>

    <main id="vitrine">
        <!-- Produtos renderizados via JS -->
    </main>

    <aside id="carrinhoLateral" class="fechado">
        <h2>Carrinho</h2>
        <div id="itensCarrinho"></div>
        <div id="totalCarrinho">Total: R$ 0,00</div>
        <button id="btnFinalizar">Finalizar compra</button>
    </aside>

    <div id="overlay"></div>
    <script src="script.js"></script>
</body>
</html>
```

2. **Definir os dados dos produtos em JavaScript** — Um array de objetos.

```js
const produtos = [
    { id: 1, nome: "Camiseta",       preco: 49.90, imagem: "https://placehold.co/200?text=Camiseta" },
    { id: 2, nome: "Calça Jeans",    preco: 129.90, imagem: "https://placehold.co/200?text=Jeans" },
    { id: 3, nome: "Tênis",          preco: 199.90, imagem: "https://placehold.co/200?text=Tenis" },
    { id: 4, nome: "Mochila",        preco: 89.90, imagem: "https://placehold.co/200?text=Mochila" },
    { id: 5, nome: "Boné",           preco: 39.90, imagem: "https://placehold.co/200?text=Bone" },
    { id: 6, nome: "Relógio",        preco: 149.90, imagem: "https://placehold.co/200?text=Relogio" },
];
```

3. **Renderizar a vitrine com Grid** — Crie os cards dinamicamente.

```js
const vitrine = document.querySelector('#vitrine');

function renderizarProdutos() {
    vitrine.innerHTML = '';
    for (const produto of produtos) {
        const card = document.createElement('div');
        card.className = 'produto';
        card.innerHTML = `
            <img src="${produto.imagem}" alt="${produto.nome}">
            <h3>${produto.nome}</h3>
            <p class="preco">R$ ${produto.preco.toFixed(2)}</p>
            <button class="btn-comprar" data-id="${produto.id}">Adicionar</button>
        `;
        vitrine.appendChild(card);
    }
}
```

4. **Gerenciar o carrinho com localStorage** — Funções para adicionar, remover, calcular.

```js
let carrinho = [];

function carregarCarrinho() {
    const dados = localStorage.getItem('carrinho');
    carrinho = dados ? JSON.parse(dados) : [];
}

function salvarCarrinho() {
    localStorage.setItem('carrinho', JSON.stringify(carrinho));
}

function adicionarAoCarrinho(produtoId) {
    const item = carrinho.find(i => i.id === produtoId);
    if (item) {
        item.quantidade++;
    } else {
        const produto = produtos.find(p => p.id === produtoId);
        carrinho.push({ ...produto, quantidade: 1 });
    }
    salvarCarrinho();
    atualizarInterface();
}

function removerDoCarrinho(produtoId) {
    carrinho = carrinho.filter(i => i.id !== produtoId);
    salvarCarrinho();
    atualizarInterface();
}

function atualizarQuantidade(produtoId, novaQtd) {
    if (novaQtd <= 0) {
        removerDoCarrinho(produtoId);
        return;
    }
    const item = carrinho.find(i => i.id === produtoId);
    if (item) {
        item.quantidade = novaQtd;
        salvarCarrinho();
        atualizarInterface();
    }
}
```

5. **Calcular total e atualizar contador** — Funções de exibição.

```js
function calcularTotal() {
    return carrinho.reduce((total, item) => total + item.preco * item.quantidade, 0);
}

function atualizarContador() {
    const totalItens = carrinho.reduce((soma, item) => soma + item.quantidade, 0);
    document.querySelector('#contador').textContent = totalItens;
}
```

6. **Renderizar itens do carrinho** — Exiba os itens no aside.

```js
function renderizarItensCarrinho() {
    const container = document.querySelector('#itensCarrinho');
    if (carrinho.length === 0) {
        container.innerHTML = '<p>Carrinho vazio</p>';
        return;
    }
    container.innerHTML = '';
    for (const item of carrinho) {
        const div = document.createElement('div');
        div.className = 'item-carrinho';
        div.innerHTML = `
            <div>
                <strong>${item.nome}</strong>
                <p>R$ ${item.preco.toFixed(2)}</p>
                <div class="qtd-controles">
                    <button class="qtd-menos" data-id="${item.id}">-</button>
                    <span>${item.quantidade}</span>
                    <button class="qtd-mais" data-id="${item.id}">+</button>
                </div>
            </div>
            <button class="btn-remover" data-id="${item.id}">🗑️</button>
        `;
        container.appendChild(div);
    }
}

function atualizarInterface() {
    atualizarContador();
    renderizarItensCarrinho();
    document.querySelector('#totalCarrinho').textContent = 
        `Total: R$ ${calcularTotal().toFixed(2)}`;
}
```

7. **Event listeners e toggle do carrinho** — Conecte tudo.

```js
vitrine.addEventListener('click', function(event) {
    if (event.target.classList.contains('btn-comprar')) {
        const id = parseInt(event.target.dataset.id);
        adicionarAoCarrinho(id);
        abrirCarrinho();
    }
});

document.querySelector('#itensCarrinho').addEventListener('click', function(event) {
    const id = parseInt(event.target.dataset.id);
    if (event.target.classList.contains('qtd-mais')) {
        const item = carrinho.find(i => i.id === id);
        atualizarQuantidade(id, item.quantidade + 1);
    }
    if (event.target.classList.contains('qtd-menos')) {
        const item = carrinho.find(i => i.id === id);
        atualizarQuantidade(id, item.quantidade - 1);
    }
    if (event.target.classList.contains('btn-remover')) {
        removerDoCarrinho(id);
    }
});

function abrirCarrinho() {
    document.querySelector('#carrinhoLateral').classList.remove('fechado');
    document.querySelector('#overlay').classList.add('ativo');
}

document.querySelector('#btnCarrinho').addEventListener('click', abrirCarrinho);
document.querySelector('#overlay').addEventListener('click', function() {
    document.querySelector('#carrinhoLateral').classList.add('fechado');
    document.querySelector('#overlay').classList.remove('ativo');
});
```

## Checkpoint

:::objetivo Você está no caminho certo se
A vitrine mostra 6 produtos com imagem e preço. Ao clicar em
Adicionar, o carrinho abre com o item. Os botões + e - alteram
quantidades. O total atualiza automaticamente. Ao recarregar a
página, os itens no carrinho permanecem.
:::

## Erros comuns

:::atencao Sintoma: ao recarregar, o carrinho aparece vazio
Causa: esqueceu de chamar carregarCarrinho() e renderizarProdutos()
na inicialização. Correção: adicione estas chamadas no início do
script, fora de qualquer função.
:::

:::atencao Sintoma: o total aparece "R$ NaN"
Causa: o preço está como string no array de produtos ou veio do
localStorage sem ser convertido para número. Correção: use
parseFloat() ou Number() ao calcular o total.
:::

## Desafio

Adicione um campo de busca que filtra produtos por nome em tempo real (use o evento input e filter do JavaScript).

:::importante Desafio extra
Para quem terminar primeiro: implemente um modal de "confirmação
de compra" que, ao clicar em Finalizar, exibe um resumo dos itens,
o total, e um botão "Confirmar" que limpa o carrinho e mostra
uma mensagem de sucesso.
:::

## Código completo

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minha Loja</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f2f5; }
        header {
            background: #1a1a2e; color: white; padding: 16px 32px;
            display: flex; justify-content: space-between; align-items: center;
            position: sticky; top: 0; z-index: 100;
        }
        #btnCarrinho { background: #2a9d8f; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 1rem; }
        #vitrine {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 20px; padding: 32px; max-width: 1200px; margin: 0 auto;
        }
        .produto {
            background: white; border-radius: 8px; padding: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center;
        }
        .produto img { max-width: 100%; height: 180px; object-fit: cover; border-radius: 4px; margin-bottom: 12px; }
        .produto h3 { margin-bottom: 8px; }
        .preco { color: #2a9d8f; font-size: 1.3rem; font-weight: bold; margin-bottom: 12px; }
        .btn-comprar { background: #2a9d8f; color: white; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; }
        #carrinhoLateral {
            position: fixed; right: 0; top: 0; width: 350px; height: 100vh;
            background: white; box-shadow: -2px 0 8px rgba(0,0,0,0.1);
            padding: 24px; z-index: 200; transition: transform 0.3s;
            display: flex; flex-direction: column;
        }
        #carrinhoLateral.fechado { transform: translateX(100%); }
        #carrinhoLateral h2 { margin-bottom: 16px; }
        #itensCarrinho { flex: 1; overflow-y: auto; }
        .item-carrinho { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #eee; }
        .qtd-controles { display: flex; align-items: center; gap: 8px; margin-top: 8px; }
        .qtd-controles button { background: #eee; border: none; width: 28px; height: 28px; border-radius: 4px; cursor: pointer; font-size: 1.1rem; }
        #totalCarrinho { font-size: 1.2rem; font-weight: bold; margin: 16px 0; }
        #btnFinalizar { background: #1a1a2e; color: white; border: none; padding: 12px; border-radius: 6px; cursor: pointer; width: 100%; }
        #overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 150; }
        #overlay.ativo { display: block; }
    </style>
</head>
<body>
    <header>
        <h1>Minha Loja</h1>
        <input type="text" id="busca" placeholder="Buscar produto..." style="padding:8px;border-radius:4px;border:none;flex:1;max-width:300px;margin:0 20px;">
        <button id="btnCarrinho">🛒 Carrinho (<span id="contador">0</span>)</button>
    </header>
    <main id="vitrine"></main>
    <aside id="carrinhoLateral" class="fechado">
        <h2>Carrinho</h2>
        <div id="itensCarrinho"><p>Carrinho vazio</p></div>
        <div id="totalCarrinho">Total: R$ 0,00</div>
        <button id="btnFinalizar">Finalizar compra</button>
    </aside>
    <div id="overlay"></div>
    <script>
        const produtos = [
            { id: 1, nome: "Camiseta",       preco: 49.90, imagem: "https://placehold.co/200?text=Camiseta" },
            { id: 2, nome: "Calça Jeans",    preco: 129.90, imagem: "https://placehold.co/200?text=Jeans" },
            { id: 3, nome: "Tênis",          preco: 199.90, imagem: "https://placehold.co/200?text=Tenis" },
            { id: 4, nome: "Mochila",        preco: 89.90, imagem: "https://placehold.co/200?text=Mochila" },
            { id: 5, nome: "Boné",           preco: 39.90, imagem: "https://placehold.co/200?text=Bone" },
            { id: 6, nome: "Relógio",        preco: 149.90, imagem: "https://placehold.co/200?text=Relogio" },
        ];

        let carrinho = [];

        function carregarCarrinho() {
            const dados = localStorage.getItem('carrinho');
            carrinho = dados ? JSON.parse(dados) : [];
        }

        function salvarCarrinho() {
            localStorage.setItem('carrinho', JSON.stringify(carrinho));
        }

        function renderizarProdutos(filtro = '') {
            const vitrine = document.querySelector('#vitrine');
            vitrine.innerHTML = '';
            const lista = filtro
                ? produtos.filter(p => p.nome.toLowerCase().includes(filtro.toLowerCase()))
                : produtos;
            for (const p of lista) {
                const card = document.createElement('div');
                card.className = 'produto';
                card.innerHTML = `<img src="${p.imagem}" alt="${p.nome}"><h3>${p.nome}</h3><p class="preco">R$ ${p.preco.toFixed(2)}</p><button class="btn-comprar" data-id="${p.id}">Adicionar</button>`;
                vitrine.appendChild(card);
            }
        }

        function adicionarAoCarrinho(id) {
            const item = carrinho.find(i => i.id === id);
            if (item) { item.quantidade++; }
            else { const p = produtos.find(x => x.id === id); carrinho.push({ ...p, quantidade: 1 }); }
            salvarCarrinho(); atualizarInterface();
        }

        function removerDoCarrinho(id) {
            carrinho = carrinho.filter(i => i.id !== id);
            salvarCarrinho(); atualizarInterface();
        }

        function atualizarQuantidade(id, qtd) {
            if (qtd <= 0) { removerDoCarrinho(id); return; }
            const item = carrinho.find(i => i.id === id);
            if (item) { item.quantidade = qtd; salvarCarrinho(); atualizarInterface(); }
        }

        function calcularTotal() {
            return carrinho.reduce((t, item) => t + item.preco * item.quantidade, 0);
        }

        function atualizarInterface() {
            const totalItens = carrinho.reduce((s, i) => s + i.quantidade, 0);
            document.querySelector('#contador').textContent = totalItens;
            const container = document.querySelector('#itensCarrinho');
            if (carrinho.length === 0) { container.innerHTML = '<p>Carrinho vazio</p>'; }
            else {
                container.innerHTML = '';
                for (const item of carrinho) {
                    const div = document.createElement('div'); div.className = 'item-carrinho';
                    div.innerHTML = `<div><strong>${item.nome}</strong><p>R$ ${item.preco.toFixed(2)}</p><div class="qtd-controles"><button class="qtd-menos" data-id="${item.id}">-</button><span>${item.quantidade}</span><button class="qtd-mais" data-id="${item.id}">+</button></div></div><button class="btn-remover" data-id="${item.id}">🗑️</button>`;
                    container.appendChild(div);
                }
            }
            document.querySelector('#totalCarrinho').textContent = `Total: R$ ${calcularTotal().toFixed(2)}`;
        }

        document.querySelector('#busca').addEventListener('input', function() {
            renderizarProdutos(this.value);
        });

        document.querySelector('#vitrine').addEventListener('click', function(e) {
            if (e.target.classList.contains('btn-comprar')) {
                adicionarAoCarrinho(parseInt(e.target.dataset.id));
                document.querySelector('#carrinhoLateral').classList.remove('fechado');
                document.querySelector('#overlay').classList.add('ativo');
            }
        });

        document.querySelector('#itensCarrinho').addEventListener('click', function(e) {
            const id = parseInt(e.target.dataset.id);
            if (e.target.classList.contains('qtd-mais')) {
                const item = carrinho.find(i => i.id === id);
                if (item) atualizarQuantidade(id, item.quantidade + 1);
            }
            if (e.target.classList.contains('qtd-menos')) {
                const item = carrinho.find(i => i.id === id);
                if (item) atualizarQuantidade(id, item.quantidade - 1);
            }
            if (e.target.classList.contains('btn-remover')) removerDoCarrinho(id);
        });

        document.querySelector('#btnCarrinho').addEventListener('click', function() {
            document.querySelector('#carrinhoLateral').classList.remove('fechado');
            document.querySelector('#overlay').classList.add('ativo');
        });

        document.querySelector('#overlay').addEventListener('click', function() {
            document.querySelector('#carrinhoLateral').classList.add('fechado');
            document.querySelector('#overlay').classList.remove('ativo');
        });

        document.querySelector('#btnFinalizar').addEventListener('click', function() {
            if (carrinho.length === 0) { alert('Carrinho vazio!'); return; }
            alert(`Compra finalizada! Total: R$ ${calcularTotal().toFixed(2)}`);
            carrinho = []; salvarCarrinho(); atualizarInterface();
            document.querySelector('#carrinhoLateral').classList.add('fechado');
            document.querySelector('#overlay').classList.remove('ativo');
        });

        carregarCarrinho();
        renderizarProdutos();
        atualizarInterface();
    </script>
</body>
</html>
```

## Fechamento

:::resumo
- Um e-commerce front-end integra HTML, CSS, JavaScript e localStorage
- Grid para vitrine, Flexbox para componentes internos
- localStorage garante persistência dos itens do carrinho
- Event delegation simplifica listeners em elementos dinâmicos
- O projeto final mostra o domínio completo do front-end estudado
- Próxima turma: Programação Back-End — lógica de programação com Python
:::
