from core.validadores import validar_markdown_aula, detectar_modo

# 1. Aula conceitual válida
VALID_CONCEITUAL = """# Aula 01 — Introdução ao DOM

O DOM (Document Object Model) é a estrutura que permite ao JavaScript manipular
elementos de uma página HTML. Nesta aula, entenderemos a árvore de objetos e como
acessar e modificar elementos básicos de forma interativa e dinâmica.

## O que é o DOM

:::conceito Árvore de Objetos
O DOM é uma representação em memória da página HTML onde cada tag vira um objeto.
:::

## Acessando elementos

:::dica document.querySelector
Use querySelector para selecionar elementos usando seletores CSS.
:::

## Questões de fixação

:::questao Qual objeto representa a página inteira no DOM?
a) window
b) document *
c) html
d) element
> O objeto document é a raiz de toda a árvore do DOM.
> É a partir dele que acessamos todos os elementos do HTML.
:::

:::questao Qual método NÃO seleciona múltiplos elementos?
a) querySelectorAll
b) getElementsByClassName
c) querySelector *
d) getElementsByTagName
> querySelector retorna apenas o primeiro elemento correspondente.
> Todos os outros métodos da lista retornam uma coleção de elementos.
:::

## Fechamento

:::resumo
- O DOM representa a página como uma árvore de objetos
- document.querySelector seleciona elementos via CSS
- querySelector retorna o primeiro elemento correspondente
- Próxima aula: Manipulação de eventos no DOM
:::
"""

# 2. Aula prática válida
VALID_PRATICA = """# Aula 02 — Contador de Cliques

Nesta aula prática, vamos construir um contador de cliques simples em HTML e JavaScript.
O objetivo é consolidar o uso de seletores e eventos de clique manipulando o DOM.
Ao final, o contador registrará e exibirá os cliques incrementados pelo usuário.

## O que vamos construir

:::objetivo Contador Funcional
Um botão que ao ser clicado atualiza o número exibido em tempo real.
:::

## Pré-requisitos

:::dica Ferramentas necessárias
Editor de código VS Code e navegador Google Chrome ou Firefox.
:::

## Passo a passo

1. **Criar o HTML** — Estruture a página com um botão e um texto.

```html
<p id="contador">0</p>
<button id="btn">Incrementar</button>
```

2. **Escrever o Script** — Selecione o botão e incremente o contador.

```js
let Cliques = 0;
const p = document.getElementById("contador");
document.getElementById("btn").addEventListener("click", () => {
    Cliques++;
    p.textContent = Cliques;
});
```

## Checkpoint

:::objetivo Contador incrementando
O texto exibe '1' após o primeiro clique no botão.
:::

## Erros comuns

:::atencao Sintoma: texto do contador não atualiza
Causa: elemento selecionado com ID incorreto.
Correção: verifique se o ID no HTML coincide com o do document.getElementById.
:::

## Código completo

```html
<!DOCTYPE html>
<html>
<body>
  <p id="contador">0</p>
  <button id="btn">Incrementar</button>
  <script>
    let Cliques = 0;
    const p = document.getElementById("contador");
    document.getElementById("btn").addEventListener("click", () => {
        Cliques++;
        p.textContent = Cliques;
    });
  </script>
</body>
</html>
```

## Fechamento

:::resumo
- Ouvimos eventos de clique com addEventListener
- Elementos são selecionados por ID
- Modificamos o conteúdo de texto com textContent
- Próxima aula: Persistência local do contador
:::
"""

def test_valid_conceptual_lesson():
    erros = validar_markdown_aula(VALID_CONCEITUAL)
    assert not erros

def test_valid_practical_lesson():
    erros = validar_markdown_aula(VALID_PRATICA)
    assert not erros

def test_empty_document():
    erros = validar_markdown_aula("")
    assert len(erros) == 1
    assert "vazio" in erros[0].lower()

def test_multiple_h1_headers():
    texto = VALID_CONCEITUAL + "\n# Outro Título H1"
    erros = validar_markdown_aula(texto)
    assert any("título H1" in e for e in erros)

def test_missing_h1():
    texto = VALID_CONCEITUAL.replace("# Aula 01 — Introdução ao DOM", "")
    erros = validar_markdown_aula(texto)
    assert any("título H1" in e for e in erros)

def test_intro_not_simple_paragraph():
    texto = """# Título

:::dica
Dica logo de início que quebra a regra de parágrafo simples.
:::

## Secao 1
## Secao 2
## Secao 3
## Secao 4
"""
    erros = validar_markdown_aula(texto)
    assert any("parágrafo simples" in e for e in erros)

def test_intro_too_short():
    texto = """# Título

Introdução curta de apenas uma linha.

## Secao 1
## Secao 2
## Secao 3
## Secao 4
"""
    erros = validar_markdown_aula(texto)
    assert any("introdutório deve ter entre 3 e 6 linhas" in e for e in erros)

def test_insufficient_h2_sections():
    texto = VALID_CONCEITUAL.replace("## O que é o DOM", "").replace("## Acessando elementos", "")
    erros = validar_markdown_aula(texto)
    assert any("seções H2" in e for e in erros)

def test_indented_h2_header():
    texto = VALID_CONCEITUAL.replace("## O que é o DOM", "  ## O que é o DOM")
    erros = validar_markdown_aula(texto)
    assert any("início da linha" in e for e in erros)

def test_too_many_list_items():
    texto = VALID_CONCEITUAL + "\n## Outra Seção\n- item 1\n- item 2\n- item 3\n- item 4\n- item 5\n- item 6\n- item 7\n"
    erros = validar_markdown_aula(texto)
    assert any("mais de 5 itens" in e for e in erros)

def test_long_code_block_outside_complete_code():
    long_code = "\n".join([f"line_{i}" for i in range(25)])
    texto = VALID_CONCEITUAL + f"\n## Outra Seção\n```js\n{long_code}\n```\n"
    erros = validar_markdown_aula(texto)
    assert any("mais de 20 linhas" in e for e in erros)

def test_raw_html_callout():
    texto = VALID_CONCEITUAL + '\n## Outra Seção\n<div class="callout c-green">Objetivo</div>'
    erros = validar_markdown_aula(texto)
    assert any("sintaxe ':::tipo'" in e for e in erros)

def test_invalid_callout_type():
    texto = VALID_CONCEITUAL + "\n## Outra Seção\n:::alerta-generico\nTexto\n:::\n"
    erros = validar_markdown_aula(texto)
    assert any("Tipo de callout inválido" in e for e in erros)

def test_question_without_correct_option():
    texto = VALID_CONCEITUAL.replace("b) document *", "b) document")
    erros = validar_markdown_aula(texto)
    assert any("uma alternativa correta" in e for e in erros)

def test_question_with_short_explanation():
    texto = VALID_CONCEITUAL.replace("> É a partir dele que acessamos todos os elementos do HTML.", "")
    erros = validar_markdown_aula(texto)
    assert any("pelo menos 2 linhas" in e for e in erros)

def test_multiple_roteiro_blocks():
    texto = VALID_CONCEITUAL + "\n:::roteiro\nFala 1\n:::\n:::roteiro\nFala 2\n:::\n"
    erros = validar_markdown_aula(texto)
    assert any("no máximo 1 bloco :::roteiro" in e for e in erros)

def test_mode_detection():
    assert detectar_modo(VALID_CONCEITUAL) == "conceitual"
    assert detectar_modo(VALID_PRATICA) == "prático"
