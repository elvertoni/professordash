# Aula 09 — DOM: Manipulando a página com JavaScript

Até agora, todo o JavaScript que escrevemos rodou no console e não interagiu com a página HTML. Nesta aula, você vai aprender a usar o DOM (Document Object Model) para selecionar elementos da página, modificar conteúdo, criar novos elementos e responder a eventos do usuário — como cliques e digitação. Vamos construir um mural de recados interativo.

## O que vamos construir

Um mural de recados onde o usuário digita uma mensagem, clica em "Publicar" e o recado aparece na tela. Dá para curtir e excluir recados. Tudo isso manipulando o DOM com JavaScript puro.

:::objetivo Resultado final
Uma página com um campo de texto, botão de publicar e uma área
de recados. Ao digitar e clicar em Publicar, o recado aparece
instantaneamente na tela, sem recarregar a página.
:::

## Pré-requisitos

:::dica Para esta aula você precisa de
HTML básico, JavaScript (variáveis, funções, eventos) e um arquivo
index.html + script.js para trabalhar. Navegador com console aberto.
:::

## Passo a passo

1. **Criar a estrutura HTML do mural** — Um formulário simples e uma área de recados.

```html



    
    
    Mural de Recados
    


    
        Mural de Recados
        
            
            Publicar
        
        
            
        
    
    


```

2. **Selecionar elementos do DOM** — Use querySelector para pegar referências aos elementos.

Abra o script.js:

```js
const campoRecado = document.querySelector('#campoRecado');
const btnPublicar = document.querySelector('#btnPublicar');
const listaRecados = document.querySelector('#listaRecados');
```

`document.querySelector` recebe um seletor CSS (mesma sintaxe) e retorna o primeiro elemento que corresponde.

3. **Adicionar evento de clique e criar recado** — Use addEventListener para responder ao clique.

```js
btnPublicar.addEventListener('click', function() {
    const texto = campoRecado.value.trim();
    if (texto === '') {
        alert('Digite um recado antes de publicar.');
        return;
    }
    
    criarRecado(texto);
    campoRecado.value = '';
    campoRecado.focus();
});
```

`addEventListener` é o método moderno para registrar eventos. O primeiro parâmetro é o tipo de evento ('click'), o segundo é a função que roda quando o evento acontece.

4. **Criar elementos dinamicamente** — A função `criarRecado` constrói o HTML do recado.

```js
function criarRecado(texto) {
    const div = document.createElement('div');
    div.className = 'recado';
    
    const paragrafo = document.createElement('p');
    paragrafo.textContent = texto;
    
    const btnCurtir = document.createElement('button');
    btnCurtir.textContent = '👍 Curtir (0)';
    btnCurtir.className = 'btn-curtir';
    
    const btnExcluir = document.createElement('button');
    btnExcluir.textContent = '🗑️ Excluir';
    btnExcluir.className = 'btn-excluir';
    
    div.appendChild(paragrafo);
    div.appendChild(btnCurtir);
    div.appendChild(btnExcluir);
    listaRecados.prepend(div);
}
```

`createElement` cria um novo elemento HTML na memória. `appendChild` insere ele como filho de outro elemento. `prepend` insere no início da lista.

5. **Adicionar funcionalidade de curtir e excluir** — Eventos nos botões recém-criados.

```js
function criarRecado(texto) {
    // ... (código anterior) ...
    
    btnCurtir.addEventListener('click', function() {
        const curtidas = btnCurtir.dataset.curtidas 
            ? parseInt(btnCurtir.dataset.curtidas) 
            : 0;
        const novasCurtidas = curtidas + 1;
        btnCurtir.dataset.curtidas = novasCurtidas;
        btnCurtir.textContent = `👍 Curtir (${novasCurtidas})`;
    });
    
    btnExcluir.addEventListener('click', function() {
        div.remove();
    });
    
    // ... (appendChild) ...
}
```

O atributo `dataset` permite armazenar dados personalizados em elementos HTML (data-curtidas no caso).

## Checkpoint

:::objetivo Você está no caminho certo se
Ao digitar um texto e clicar em Publicar, o recado aparece na
lista. Ao clicar em Curtir, o contador aumenta. Ao clicar em
Excluir, o recado some. O campo de texto fica vazio após publicar.
:::

## Erros comuns

:::atencao Sintoma: ao clicar em Publicar, a página recarrega
Causa: o botão está dentro de um form e dispara submit.
Correção: use  ou adicione
event.preventDefault() no listener. Botões dentro de form têm
type="submit" por padrão.
:::

:::atencao Sintoma: o recado não aparece na tela
Causa: o elemento #listaRecados não existe no HTML quando o script
roda, ou o querySelector retornou null.
Correção: coloque a tag  no final do body (depois do HTML)
ou use DOMContentLoaded para garantir que o DOM foi carregado.
:::

## Desafio

Adicione um contador de caracteres no campo de texto que mostra "X/140 caracteres" e bloqueia a publicação se ultrapassar 140.

:::importante Desafio extra
Para quem terminar primeiro: adicione um efeito de fade-in nos
recados novos usando a propriedade CSS opacity e a API
requestAnimationFrame ou uma classe CSS com transition.
:::

## Código completo

```html



    
    
    Mural de Recados
    
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f2f5; padding: 40px 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { color: #1a1a2e; margin-bottom: 20px; }
        .form-group { display: flex; gap: 8px; margin-bottom: 24px; }
        #campoRecado {
            flex: 1; padding: 10px; border: 2px solid #ddd;
            border-radius: 6px; font-size: 1rem;
        }
        #btnPublicar {
            background: #2a9d8f; color: white; border: none;
            padding: 10px 20px; border-radius: 6px; cursor: pointer;
        }
        #btnPublicar:hover { background: #21867a; }
        .recado {
            background: white; padding: 16px;
            border-radius: 6px; margin-bottom: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .recado p { margin-bottom: 12px; color: #333; }
        .recado button {
            border: none; padding: 6px 12px; border-radius: 4px;
            cursor: pointer; margin-right: 6px; font-size: 0.9rem;
        }
        .btn-curtir { background: #e8f5e9; }
        .btn-excluir { background: #ffebee; }
    


    
        Mural de Recados
        
            
            Publicar
        
        
    
    
        const campoRecado = document.querySelector('#campoRecado');
        const btnPublicar = document.querySelector('#btnPublicar');
        const listaRecados = document.querySelector('#listaRecados');

        function criarRecado(texto) {
            const div = document.createElement('div');
            div.className = 'recado';
            
            const paragrafo = document.createElement('p');
            paragrafo.textContent = texto;
            
            const btnCurtir = document.createElement('button');
            btnCurtir.textContent = '👍 Curtir (0)';
            btnCurtir.className = 'btn-curtir';
            
            const btnExcluir = document.createElement('button');
            btnExcluir.textContent = '🗑️ Excluir';
            btnExcluir.className = 'btn-excluir';
            
            btnCurtir.addEventListener('click', function() {
                const curtidas = btnCurtir.dataset.curtidas 
                    ? parseInt(btnCurtir.dataset.curtidas) : 0;
                btnCurtir.dataset.curtidas = curtidas + 1;
                btnCurtir.textContent = `👍 Curtir (${curtidas + 1})`;
            });
            
            btnExcluir.addEventListener('click', function() {
                div.remove();
            });
            
            div.appendChild(paragrafo);
            div.appendChild(btnCurtir);
            div.appendChild(btnExcluir);
            listaRecados.prepend(div);
        }

        btnPublicar.addEventListener('click', function() {
            const texto = campoRecado.value.trim();
            if (texto === '') {
                alert('Digite um recado antes de publicar.');
                return;
            }
            criarRecado(texto);
            campoRecado.value = '';
            campoRecado.focus();
        });
    


```

## Fechamento

:::resumo
- DOM (Document Object Model) é a representação da página como uma árvore de objetos
- document.querySelector(seletor) seleciona elementos com sintaxe CSS
- createElement cria novos elementos; appendChild e prepend os inserem
- addEventListener registra funções para responder a eventos do usuário
- dataset armazena dados personalizados em elementos HTML
- Próxima aula: formulários HTML e validação
:::
