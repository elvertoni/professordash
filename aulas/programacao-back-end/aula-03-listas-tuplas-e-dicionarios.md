# Aula 03 — Listas, tuplas e dicionários

Você já sabe declarar variáveis e usar condicionais e loops em Python. Mas e quando você precisa guardar não um único valor, mas uma coleção deles — como as notas de um aluno, os nomes de uma turma ou o estoque de produtos? Python oferece estruturas de dados nativas poderosas para organizar informações. Nesta aula conceitual, vamos conhecer listas, tuplas e dicionários — as três estruturas de coleção que você mais usará no dia a dia.

## Listas — coleções mutáveis e ordenadas

Uma lista em Python é uma coleção ordenada de elementos que pode ser modificada (mutável). É a estrutura mais versátil e mais usada na linguagem.

:::conceito Listas em Python
Criadas com colchetes [] ou com list(). São mutáveis (podemos
adicionar, remover e alterar elementos), ordenadas (os índices
começam em 0), permitem elementos duplicados e aceitam qualquer
tipo de dado misturado.
:::

```python
frutas = ["maçã", "banana", "laranja"]
print(frutas[0])       # maçã
frutas.append("uva")   # adiciona no final
frutas.insert(1, "kiwi") # insere na posição 1
frutas.remove("banana") # remove pelo valor
print(len(frutas))     # tamanho da lista
```

:::exemplo Operações comuns com listas
```python
numeros = [4, 2, 9, 1, 5]
numeros.sort()        # ordena in-place: [1, 2, 4, 5, 9]
numeros.reverse()     # inverte a ordem
soma = sum(numeros)   # 21
maior = max(numeros)  # 9
menor = min(numeros)  # 1

### Fatiamento (slicing) — [inicio:fim:passo]
print(numeros[1:4])   # [2, 4, 5]
print(numeros[::-1])  # lista invertida
```
:::

O fatiamento é uma das características mais elegantes do Python. A sintaxe `lista[inicio:fim:passo]` permite extrair sublistas de forma intuitiva.

## Tuplas — coleções imutáveis

Tuplas são como listas, mas não podem ser modificadas depois de criadas. Isso as torna seguras para dados que não devem mudar acidentalmente.

:::importante Tuplas vs Listas
Tuplas usam parênteses () em vez de colchetes. São imutáveis —
não é possível adicionar, remover ou alterar elementos. Vantagens:
ocupam menos memória, são mais rápidas e protegem dados contra
modificação acidental. Use tuplas para coordenadas, datas,
configurações fixas e chaves de dicionário.
:::

```python
coordenadas = (-23.55, -46.63)  # latitude, longitude (imutável)
cores_rgb = (255, 0, 0)          # vermelho em RGB

### Desempacotamento automático
x, y = coordenadas
print(f"Latitude: {x}, Longitude: {y}")

### Tentar modificar dá erro:
### coordenadas[0] = 0  # TypeError: 'tuple' object does not support item assignment
```

O desempacotamento de tuplas é um recurso que permite atribuir múltiplas variáveis de uma só vez — muito usado em loops e retorno de funções.

## Dicionários — pares chave-valor

Dicionários armazenam dados associativos: cada elemento tem uma chave única e um valor correspondente. São a estrutura mais importante para dados estruturados em Python.

:::conceito Dicionários
Criados com chaves {} ou dict(). Cada elemento é um par
chave: valor. As chaves devem ser imutáveis (string, número,
tupla) e únicas. Valores podem ser qualquer tipo. São a base
para representar objetos JSON e dados de APIs.
:::

```python
aluno = {
    "nome": "Ana Silva",
    "idade": 17,
    "notas": [8, 7, 9],
    "aprovado": True
}

print(aluno["nome"])        # Ana Silva
print(aluno.get("turma", "Não informada"))  # valor padrão
aluno["idade"] = 18         # altera valor
aluno["turma"] = "PFE-2A"  # adiciona nova chave

for chave, valor in aluno.items():
    print(f"{chave}: {valor}")
```

:::exemplo Combinando estruturas
Dicionários podem conter listas, listas podem conter dicionários
— a composição é livre e extremamente comum:

```python
turma = [
    {"nome": "Ana",   "notas": [8, 7, 9]},
    {"nome": "Bruno", "notas": [6, 5, 7]},
    {"nome": "Carla", "notas": [10, 9, 8]},
]

### Média de todas as notas da turma
for aluno in turma:
    media = sum(aluno["notas"]) / len(aluno["notas"])
    print(f"{aluno['nome']}: {media:.1f}")
```
:::

## Qual estrutura usar?

A escolha certa depende do problema que você está resolvendo.

:::importante Guia de decisão
Lista: quando a ordem importa e você precisa adicionar/remover
itens dinamicamente (lista de alunos, tarefas, resultados).
Tupla: quando os dados são fixos e imutáveis (dias da semana,
coordenadas, configurações constantes).
Dicionário: quando você precisa associar chaves a valores
(cadastro de aluno, estoque de produtos, resposta de API).
:::

## Questões de fixação

:::questao Qual a diferença fundamental entre uma lista e uma tupla em Python?
a) Listas usam [] e tuplas usam {}
b) Listas são mutáveis; tuplas são imutáveis *
c) Tuplas aceitam qualquer tipo; listas só um tipo
d) Listas são mais rápidas que tuplas
> A diferença essencial é que listas podem ser modificadas após
> a criação (append, remove, alteração de índices), enquanto tuplas
> são imutáveis — uma vez criadas, não mudam. Os parênteses das
> tuplas são opcionais em muitos contextos, e colchetes são das listas.
> Ambos aceitam tipos mistos, e tuplas são ligeiramente mais rápidas.
:::

:::questao Qual método NÃO pode ser usado para adicionar um elemento a uma lista?
a) .append()
b) .insert()
c) .extend()
d) .add() *
> O método .add() pertence aos conjuntos (set), não às listas.
> .append() adiciona ao final, .insert() insere em posição específica,
> e .extend() adiciona todos os elementos de outro iterável ao final.
:::

## Atividade prática

Crie um programa que gerencia um pequeno estoque de produtos usando um dicionário. Cada produto tem nome, quantidade e preço. O programa deve permitir: adicionar produto, listar todos, buscar por nome, calcular valor total do estoque e remover produto.

:::objetivo Entrega
Arquivo estoque.py com as funções: adicionar(), listar(),
buscar(), valor_total() e remover(). Use um dicionário como
estrutura principal. Teste cada função com pelo menos 3 produtos.
:::

## Fechamento

:::resumo
- Listas [] são coleções mutáveis, ordenadas e versáteis
- Tuplas () são imutáveis — protegem dados contra alteração
- Dicionários {} associam chaves únicas a valores
- Slicing [inicio:fim:passo] extrai sublistas com elegância
- A composição de estruturas (lista de dicionários) é a base de dados estruturados
- Próxima aula: funções — modularização e reuso de código
:::
