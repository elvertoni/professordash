# Aula 04 — Funções: modularização e reuso

Conforme seus programas crescem, repetir o mesmo código várias vezes se
torna um problema. Se você precisa calcular o IMC de 10 alunos diferentes,
vai escrever a mesma fórmula 10 vezes? Claro que não. Funções são blocos
de código nomeados que executam uma tarefa específica e podem ser chamados
de qualquer lugar do programa. Nesta aula prática, você vai aprender a
criar, parametrizar e reutilizar funções em Python.

## O que vamos construir

Uma calculadora de IMC (Índice de Massa Corporal) completa, com funções separadas para cálculo, classificação, validação de entrada e exibição de resultados.

:::objetivo Resultado final
Um programa que pergunta peso e altura, calcula o IMC, classifica
o resultado (abaixo do peso, normal, sobrepeso, obesidade) e exibe
uma tabela com o historico de consultas do usuario.
:::

## Pré-requisitos

:::dica Para esta aula voce precisa de
Python 3 instalado, editor de texto e saber usar input(), print(),
condicionais if/elif/else e a sintaxe basica de funcoes.
:::

## Passo a passo

1. **Sintaxe básica de funções** — Use `def` para declarar, nome seguido de parênteses e dois pontos.

```python
def saudacao():
    """Exibe uma mensagem de boas-vindas."""
    print("=" * 40)
    print("     CALCULADORA DE IMC")
    print("=" * 40)
```

2. **Funções com parâmetros e retorno** — Parâmetros são entradas; `return` devolve um valor.

```python
def calcular_imc(peso, altura):
    imc = peso / (altura ** 2)
    return round(imc, 2)

def classificar_imc(imc):
    if imc < 18.5:
        return "Abaixo do peso"
    elif imc < 25:
        return "Peso normal"
    elif imc < 30:
        return "Sobrepeso"
    elif imc < 35:
        return "Obesidade grau I"
    else:
        return "Obesidade grau II ou III"
```

3. **Funções com parâmetros opcionais** — Valores padrão tornam parâmetros opcionais.

```python
def exibir_resultado(imc, nome="Usuario"):
    classificacao = classificar_imc(imc)
    print(f"\n{nome}, seu IMC e {imc:.1f}")
    print(f"Classificacao: {classificacao}")
    return classificacao
```

4. **Validação com funções** — Separe a lógica de validação em funções específicas.

```python
def ler_peso():
    while True:
        try:
            peso = float(input("Digite seu peso (kg): "))
            if 1 <= peso <= 500:
                return peso
            print("Peso invalido (1-500 kg).")
        except ValueError:
            print("Digite um numero valido.")
```

## Checkpoint

:::objetivo Voce esta no caminho certo se
O programa exibe o banner, pergunta nome, peso e altura, valida
entradas invalidas (texto, numeros negativos), calcula o IMC
corretamente e exibe a classificacao. Teste com peso 70 e altura 1.75
— deve dar IMC 22.86 e resultado "Peso normal".
:::

## Erros comuns

:::atencao Sintoma: a funcao retorna None em vez do valor esperado
Causa: voce esqueceu a palavra return — sem ela, a funcao executa
o codigo mas nao devolve nada. Correcao: adicione return valor no
final da funcao.
:::

:::atencao Sintoma: NameError variavel nao definida
Causa: a variavel foi criada dentro de uma funcao (escopo local) mas
voce tentou usa-la fora. Correcao: variaveis definidas dentro de
funcoes nao existem fora delas. Use parametros e retorno para
comunicar dados.
:::

## Desafio

Adicione uma função `recomendacao(imc)` que, baseada na classificação, sugira ações práticas (ex.: "Consulte um nutricionista" para sobrepeso, "Mantenha a alimentação" para peso normal).

:::importante Desafio extra
Crie uma funcao historico() que armazena os resultados de varias
consultas em uma lista de dicionarios e exibe um historico formatado.
:::

## Código completo

```python
def saudacao():
    print("=" * 40)
    print("     CALCULADORA DE IMC")
    print("=" * 40)

def linha():
    print("-" * 40)

def calcular_imc(peso, altura):
    return round(peso / (altura ** 2), 2)

def classificar_imc(imc):
    if imc < 18.5:
        return "Abaixo do peso"
    elif imc < 25:
        return "Peso normal"
    elif imc < 30:
        return "Sobrepeso"
    elif imc < 35:
        return "Obesidade grau I"
    else:
        return "Obesidade grau II ou III"

def recomendacao(imc):
    if imc < 18.5:
        return "Procure um nutricionista para avaliar sua alimentacao."
    elif imc < 25:
        return "Mantenha uma alimentacao equilibrada e pratique exercicios."
    elif imc < 30:
        return "Considere acompanhamento profissional."
    else:
        return "Busque orientacao medica para um plano de saude."

def ler_peso():
    while True:
        try:
            peso = float(input("Peso (kg): "))
            if 1 <= peso <= 500:
                return peso
            print("Peso invalido (1-500 kg).")
        except ValueError:
            print("Digite um numero valido.")

def ler_altura():
    while True:
        try:
            altura = float(input("Altura (m): "))
            if 0.5 <= altura <= 3:
                return altura
            print("Altura invalida (0.5-3 m).")
        except ValueError:
            print("Digite um numero valido.")

def exibir_resultado(imc, nome, classificacao, rec):
    print(f"\n{nome}, seu IMC e {imc}")
    print(f"Classificacao: {classificacao}")
    print(f"Recomendacao: {rec}")

def main():
    saudacao()
    nome = input("\nNome: ")
    peso = ler_peso()
    altura = ler_altura()
    imc = calcular_imc(peso, altura)
    classe = classificar_imc(imc)
    rec = recomendacao(imc)
    exibir_resultado(imc, nome, classe, rec)
    linha()

if __name__ == "__main__":
    main()
```

## Fechamento

:::resumo
- Funcoes sao blocos de codigo reutilizaveis declarados com def
- Parametros sao entradas da funcao; return devolve o resultado
- Parametros podem ter valores padrao para serem opcionais
- Variaveis dentro de funcoes tem escopo local (nao vazam para fora)
- Proxima aula: manipulacao de arquivos e tratamento de excecoes
:::
