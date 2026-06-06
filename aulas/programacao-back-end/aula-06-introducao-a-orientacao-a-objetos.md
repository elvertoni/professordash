# Aula 06 — Introdução à orientação a objetos

Você já usou objetos em Python sem perceber — listas, dicionários, strings: tudo em Python é um objeto. Mas o que exatamente significa "orientação a objetos"? É um paradigma de programação que organiza o código em torno de "objetos" que combinam dados (atributos) e comportamentos (métodos). Nesta aula conceitual, vamos entender os pilares da orientação a objetos: classes, objetos, atributos, métodos e encapsulamento.

## O que é uma classe? O que é um objeto?

Uma classe é como um molde ou uma planta baixa. O objeto é a construção concreta feita a partir desse molde. Se "Aluno" é a classe, então "Ana Silva, 17 anos, PFE-2A" é um objeto (uma instância) dessa classe.

:::conceito Classe vs Objeto
Classe: definição abstrata que descreve atributos (características)
e métodos (comportamentos) comuns a todos os objetos daquele tipo.
Objeto (ou instância): representação concreta de uma classe, com
valores específicos para cada atributo e capacidade de executar
os métodos definidos na classe.
:::

```python
# Definição da classe (molde)
class Aluno:
    def __init__(self, nome, idade, curso):
        self.nome = nome
        self.idade = idade
        self.curso = curso
    
    def apresentar(self):
        return f"Olá, sou {self.nome}, tenho {self.idade} anos e estudo {self.curso}."

# Criação de objetos (instâncias)
aluno1 = Aluno("Ana", 17, "Front-End")
aluno2 = Aluno("Bruno", 16, "Back-End")

print(aluno1.apresentar())  # Olá, sou Ana, tenho 17 anos e estudo Front-End.
```

## O método construtor __init__

O método `__init__` é o construtor da classe — ele roda automaticamente quando um novo objeto é criado. É nele que você inicializa os atributos do objeto.

:::importante Self — a referência ao próprio objeto
O primeiro parâmetro de todo método de instância é self, que
representa o próprio objeto. Quando você chama aluno1.apresentar(),
o Python transforma internamente em Aluno.apresentar(aluno1).
Por isso o self precisa estar sempre lá — sem ele, o método não
sabe qual objeto está sendo manipulado.
:::

```python
class ContaBancaria:
    def __init__(self, titular, saldo_inicial=0):
        self.titular = titular
        self.saldo = saldo_inicial
        self.ativa = True
    
    def depositar(self, valor):
        if valor > 0:
            self.saldo += valor
            return f"Depósito de R${valor:.2f} realizado. Saldo: R${self.saldo:.2f}"
        return "Valor inválido."
    
    def sacar(self, valor):
        if not self.ativa:
            return "Conta inativa."
        if 0  self é a referência ao próprio objeto (instância) que está
> chamando o método. Quando fazemos obj.metodo(), o Python
> traduz para Classe.metodo(obj), passando obj como self.
> Sem self, o método não consegue acessar os atributos da
> instância específica.
:::

:::questao Qual benefício NÃO é proporcionado pelo encapsulamento?
a) Proteger dados contra modificações acidentais
b) Ocultar detalhes internos da implementação
c) Aumentar a velocidade de execução do código *
d) Permitir validação de dados antes de atribuir
> Encapsulamento não tem relação com performance. Seu objetivo
> é proteger dados, esconder complexidade e permitir validação
> controlada através de getters e setters. A velocidade de
> execução é influenciada por outros fatores como algoritmos
> e estruturas de dados.
:::

## Atividade prática

Crie uma classe `Livro` com atributos titulo, autor, ano, emprestado (booleano). Adicione métodos: emprestar() (muda status para True se disponível), devolver() (muda para False), e info() que retorna uma string formatada. Crie 3 livros e simule empréstimos.

:::objetivo Entrega
Arquivo biblioteca.py com a classe Livro e um bloco de teste
que cria 3 livros, empresta 2, devolve 1 e exibe o status de
cada um no final. Use @property para o status de disponibilidade.
:::

:::roteiro
Pessoal, pensem em como uma biblioteca real funciona. Cada livro
tem dados fixos (título, autor) e um estado mutável (emprestado
ou não). A classe Livro é o molde; cada livro na estante é um
objeto. Isso é orientação a objetos na prática.
:::

## Fechamento

:::resumo
- Classe é o molde; objeto é a instância concreta
- __init__ é o construtor que inicializa atributos
- self representa o próprio objeto dentro dos métodos
- Encapsulamento protege dados com _ convenção e @property
- @classmethod e @staticmethod criam métodos sem necessidade de instância
- Próxima aula: herança, polimorfismo e duck typing
:::
