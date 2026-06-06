# Aula 02 — Estruturas condicionais e repetição

Nem todo código é executado em linha reta. Muitas vezes você precisa tomar
decisões (se a nota for maior que 6, aprovar; senão, reprovar) ou repetir
ações (exibir a tabuada do 1 ao 10). É aí que entram as estruturas
condicionais e de repetição — os blocos fundamentais que dão inteligência
ao seu programa. Nesta aula prática, você vai dominar if, elif, else,
while e for em Python.

## O que vamos construir

Um programa interativo de quiz com perguntas de múltipla escolha, contagem de acertos e repetição das perguntas que o usuário errou.

:::objetivo Resultado final
Um programa Python que faz 8 perguntas ao usuario, contabiliza os
acertos, exibe o resultado final e, se o usuario quiser, repete as
perguntas que ele errou ate acertar todas.
:::

## Pré-requisitos

:::dica Para esta aula voce precisa de
Python 3 instalado no computador, editor de texto e o arquivo
calculadora_media.py da aula anterior como referencia de sintaxe.
:::

## Passo a passo

1. **Estrutura condicional completa** — Veja como `if`, `elif` e `else` trabalham juntos.

```python
nota = float(input("Digite a nota: "))
if nota >= 9:
    conceito = "Excelente"
elif nota >= 7:
    conceito = "Bom"
elif nota >= 5:
    conceito = "Regular"
else:
    conceito = "Precisa melhorar"
print(f"Conceito: {conceito}")
```

2. **Loop `for` com `range()`** — O `for` percorre uma sequência.

```python
for i in range(1, 11):
    print(i, end=" ")
numero = int(input("Qual tabuada voce quer ver? "))
for i in range(1, 11):
    print(f"{numero} x {i} = {numero * i}")
```

3. **Loop `while`** — Repete enquanto a condição for verdadeira. Cuidado com loops infinitos!

```python
contador = 10
while contador >= 0:
    print(contador)
    contador -= 1
print("Fogo!")
senha = ""
while senha != "1234":
    senha = input("Digite a senha: ")
print("Acesso concedido!")
```

## Checkpoint

:::objetivo Voce esta no caminho certo se
O programa pergunta as questoes, responde Correto! ou Errado!
para cada uma, e no final exibe quantas voce acertou e o percentual.
Teste com respostas certas e erradas propositalmente.
:::

## Erros comuns

:::atencao Sintoma: o loop executa infinitamente
Causa: a condicao do while nunca fica falsa — a variavel de controle
nao e atualizada dentro do loop. Correcao: garanta que algo muda dentro
do loop (ex.: contador -= 1) que eventualmente torne a condicao falsa.
:::

:::atencao Sintoma: if parece nao funcionar
Causa: voce esqueceu os dois pontos no final da linha do if, ou a
indentacao esta incorreta. Em Python, indentacao e obrigatoria e
define blocos de codigo. Use 4 espacos de forma consistente.
:::

## Desafio

Adicione um placar: use um dicionário para armazenar quantas vezes o usuário acertou cada pergunta, e ao final exiba um ranking de quais perguntas foram mais fáceis e mais difíceis.

:::importante Desafio extra
Implemente uma logica com while e uma lista para permitir que o
usuario revise APENAS as perguntas que errou, repetindo ate acertar
todas. Use o break para sair se ele quiser desistir.
:::

## Código completo

```python
acertos = 0
total = 8
erradas = []
perguntas = [
    ("Qual a capital do Brasil?", "Brasilia"),
    ("Quanto e 7 x 8?", "56"),
    ("Qual o maior planeta do sistema solar?", "Jupiter"),
    ("Em que ano o Brasil foi descoberto?", "1500"),
    ("Qual a linguagem que estamos aprendendo?", "Python"),
    ("Qual o simbolo quimico da agua?", "H2O"),
    ("Em qual continente fica o Egito?", "Africa"),
    ("Quantos lados tem um hexagono?", "6"),
]
for pergunta, resposta_certa in perguntas:
    resposta = input(f"{pergunta} ")
    if resposta.lower() == resposta_certa.lower():
        print("Correto!")
        acertos += 1
    else:
        print(f"Errado! A resposta era {resposta_certa}.")
        erradas.append((pergunta, resposta_certa))
print(f"\nVoce acertou {acertos} de {total}!")
while erradas:
    print(f"\n--- Revisao: {len(erradas)} pergunta(s) errada(s) ---")
    continuar = input("Quer tentar de novo? (s/n) ")
    if continuar.lower() != "s":
        break
    acertos_revisao = 0
    novas_erradas = []
    for pergunta, resposta_certa in erradas:
        resposta = input(f"{pergunta} ")
        if resposta.lower() == resposta_certa.lower():
            print("Correto!")
            acertos_revisao += 1
        else:
            print(f"Errado! Ainda e {resposta_certa}.")
            novas_erradas.append((pergunta, resposta_certa))
    erradas = novas_erradas
    print(f"Acertou {acertos_revisao} na revisao.")
print("Fim do quiz! Parabens pelo estudo.")
```

## Fechamento

:::resumo
- if/elif/else tomam decisoes com base em condicoes booleanas
- for percorre sequencias fixas; while repete enquanto condicao
  for verdadeira
- range(inicio, fim, passo) gera sequencias numericas
- break interrompe um loop; continue pula para a proxima iteracao
- Proxima aula: listas, tuplas e dicionarios
:::
