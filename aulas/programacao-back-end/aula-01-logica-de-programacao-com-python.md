# Aula 01 — Lógica de Programação com Python

Antes de escrever código em qualquer linguagem, você precisa desenvolver o
raciocínio lógico por trás dos programas. Programar é essencialmente ensinar
o computador a resolver problemas através de instruções passo a passo.
Nesta aula, vamos aprender os fundamentos do pensamento computacional e
aplicar esses conceitos usando Python — uma linguagem clara, legível e
amplamente usada no mercado.

## O que é um algoritmo

Um algoritmo é uma sequência finita de passos bem definidos para resolver um problema. Você já usa algoritmos no dia a dia: uma receita de bolo, as instruções de montagem de um móvel, o passo a passo para resolver uma equação. A diferença é que um algoritmo computacional precisa ser preciso e sem ambiguidades.

:::conceito Algoritmo
Sequencia ordenada, finita e nao ambigua de instrucoes que, quando
executadas, produzem um resultado esperado. Exemplo: se a media for
maior ou igual a 6, exiba Aprovado; caso contrario, exiba Recuperacao.
:::

## Variáveis e tipos de dados em Python

Variáveis são como caixinhas onde guardamos informações. Em Python, você não precisa declarar o tipo explicitamente — a linguagem descobre sozinha.

```python
nome = "Maria"
idade = 17
altura = 1.65
estudante = True
```

:::importante Tipagem dinamica vs Estatica
Python tem tipagem dinamica: uma mesma variavel pode mudar de tipo
durante a execucao. Isso da flexibilidade mas exige cuidado. Em
linguagens como Java ou C, o tipo e fixo apos declarado.
:::

## Entrada e saída de dados

Para um programa interagir com o usuário, precisamos de entrada (o que o usuário digita) e saída (o que o programa exibe).

```python
nome = input("Digite seu nome: ")
print("Ola,", nome)
print(f"Bem-vindo ao curso, {nome}!")
idade = int(input("Digite sua idade: "))
ano_nascimento = 2026 - idade
print(f"Voce nasceu em {ano_nascimento}.")
```

:::dica Dica sobre f-strings
Desde o Python 3.6, as f-strings sao a forma mais legivel de formatar
texto. Basta colocar um f antes das aspas e usar chaves com o nome
da variavel para inserir valores.
:::

## Operadores básicos

Python oferece operadores aritméticos, relacionais e lógicos essenciais para construir expressões.

:::conceito Operadores em Python
Aritmeticos: + - * / (divisao real), // (divisao inteira),
% (resto/modulo), elevado a (**).
Relacionais: igual ==, diferente !=, maior >, menor =, menor ou igual 

```python
a = 10
b = 3
print(a + b)
print(a / b)
print(a // b)
print(a % b)
print(a ** b)
```
:::

## Questões de fixação

:::questao Qual operador Python calcula o resto de uma divisao inteira?
a) /
b) //
c) % *
d) potencia
> O operador % (modulo) retorna o resto da divisao entre dois numeros.
> / faz divisao real com resultado decimal, // faz divisao inteira
> (trunca o resultado), e o operador de potencia e elevado ao. O resto e especialmente
> util para verificar se um numero e par (x % 2 == 0).
:::

:::questao Qual das alternativas NAO e um tipo de dado nativo do Python?
a) int
b) float
c) str
d) char *
> Python nao tem o tipo char (caractere unico) como nativo — ele trata
> caracteres individuais como strings de comprimento 1. Os tipos nativos
> basicos sao int (inteiro), float (decimal), str (string/texto) e bool
> (logico True/False). O tipo char existe em linguagens como C e Java.
:::

## Atividade prática

Crie um programa em Python que calcula a média de três notas e informa se o aluno está aprovado (média >= 6), em recuperação (média entre 4 e 5.9) ou reprovado (média = 6:
    print("Aprovado!")
elif media >= 4:
    print("Recuperacao.")
else:
    print("Reprovado.")

:::objetivo Entrega
Salve o programa como calculadora_media.py, execute com Python e
teste com tres conjuntos de notas: (7, 8, 9), (5, 4, 6) e (2, 3, 1).
Print do terminal com os resultados. Entregue via upload no
ProfessorDash.
:::

## Fechamento

:::resumo
- Algoritmo e uma sequencia de passos para resolver um problema
- Variaveis armazenam dados; Python tem tipagem dinamica
- Tipos basicos: int, float, str, bool
- input() captura dados; print() exibe resultados
- Proxima aula: estruturas condicionais e repeticao em Python
:::
