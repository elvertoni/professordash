# Aula 02 — Modelagem conceitual: DER e entidades

Antes de escrever uma linha de SQL, é preciso planejar como os dados serão organizados. A modelagem conceitual é a primeira etapa desse planejamento: criamos um diagrama abstrato que representa as entidades do mundo real (alunos, livros, empréstimos) e como elas se relacionam, sem preocupação com tecnologia ou banco de dados específico. O resultado é o Diagrama Entidade-Relacionamento (DER).

## O que é um Diagrama Entidade-Relacionamento?

O DER é uma representação gráfica que usa símbolos padronizados para descrever a estrutura de um banco de dados. Criado por Peter Chen em 1976, ele é a ponte entre o mundo real e o modelo lógico que será implementado no banco.

:::conceito Componentes do DER
Entidade: objeto do mundo real sobre o qual queremos armazenar
dados (retângulo). Atributo: propriedade de uma entidade (elipse).
Relacionamento: associação entre duas ou mais entidades (losango).
Cardinalidade: quantas vezes uma entidade participa do
relacionamento (1:1, 1:N, N:N).
:::

Uma entidade forte (rectângulo de linha simples) existe por si só — como ALUNO ou LIVRO. Uma entidade fraca (retângulo duplo) depende de outra para existir — como DEPENDENTE (depende de FUNCIONÁRIO).

## Identificando entidades e atributos

O primeiro passo da modelagem é identificar quais são as entidades do sistema e quais atributos cada uma precisa ter.

:::exemplo Sistema de biblioteca escolar
Entidades identificadas:
ALUNO — quem pega livros emprestados
LIVRO — o que é emprestado
EMPRESTIMO — a transação de empréstimo

Atributos de ALUNO: matricula (identificador), nome, email, telefone
Atributos de LIVRO: ISBN (identificador), titulo, autor, ano
Atributos de EMPRESTIMO: id (identificador), data_retirada,
data_devolucao, status
:::

Cada entidade precisa de um atributo (ou combinação) que a identifique unicamente — a chave primária conceitual. No DER, a chave primária é sublinhada.

## Tipos de relacionamento e cardinalidade

Os relacionamentos descrevem como as entidades se conectam. A cardinalidade define quantas ocorrências de uma entidade se relacionam com a outra.

:::importante Cardinalidades fundamentais
1:1 (um para um): um aluno tem um crachá; um crachá pertence a
um aluno.
1:N (um para muitos): um professor orienta vários alunos; cada
aluno tem um orientador.
N:N (muitos para muitos): um aluno cursa várias disciplinas; uma
disciplina tem vários alunos. No banco relacional, vira tabela
intermediária.
:::

:::exemplo Lendo cardinalidades no DER
```
ALUNO ---(1,N)--- cursa ---(1,N)--- DISCIPLINA
```
Lê-se: "Um aluno cursa uma ou mais disciplinas; uma disciplina
é cursada por um ou mais alunos." O (1,N) do lado do ALUNO
significa "cada disciplina é cursada por no mínimo 1 e no máximo
N alunos". O N representa "muitos" (qualquer quantidade).
:::

## Atributos multivalorados, derivados e compostos

Nem todo atributo é simples. Alguns exigem modelagem especial.

:::conceito Tipos especiais de atributos
Composto: pode ser dividido em sub-atributos. Ex.: endereço →
(logradouro, numero, cidade, CEP). Multivalorado: pode ter
mais de um valor. Ex.: telefone (o aluno pode ter vários).
Representado com elipse dupla. Derivado: calculado a partir
de outros atributos. Ex.: idade (derivada de data_nascimento).
Representado com elipse tracejada.
:::

Atributos multivalorados na prática viram tabelas separadas na modelagem lógica. Por exemplo, em vez de vários campos telefone1, telefone2, telefone3, criamos uma tabela TELEFONE relacionada a ALUNO.

## Questões de fixação

:::questao Em um DER, qual símbolo representa um relacionamento entre entidades?
a) Retângulo
b) Elipse
c) Losango *
d) Linha tracejada
> No DER padronizado por Peter Chen, o losango representa o
> relacionamento entre entidades. O retângulo representa
> entidade, a elipse representa atributo, e as linhas conectam
> os componentes com as cardinalidades indicadas nas pontas.
:::

:::questao Qual situação NÃO é representada corretamente por uma cardinalidade 1:N?
a) Um departamento tem vários funcionários
b) Um pedido contém vários produtos *
c) Um cliente faz vários pedidos
d) Um estado tem várias cidades
> A relação entre pedido e produto é N:N (muitos para muitos),
> não 1:N. Um pedido pode conter vários produtos, e um produto
> pode estar em vários pedidos. Isso exige uma tabela
> intermediária (item_pedido). As demais opções são exemplos
> clássicos de 1:N.
:::

## Atividade prática

Crie o DER conceitual de um sistema para uma clínica médica. Identifique as entidades: PACIENTE, MEDICO, CONSULTA, RECEITA. Defina os atributos de cada uma, os relacionamentos e as cardinalidades. Desenhe o diagrama no papel ou em ferramenta digital (draw.io, Lucidchart).

:::objetivo Entrega
Diagrama completo com: 4 entidades, atributos essenciais (incluindo
chaves primárias), relacionamentos com cardinalidades corretas.
Entregue como foto do caderno, arquivo de imagem ou descrição
textual com a notação. Inclua pelo menos um atributo composto
(endereço do paciente) e um multivalorado (telefone).
:::

:::roteiro
Pessoal, a chave do DER é pensar em substantivos e verbos. Os
substantivos viram entidades: paciente, médico. Os verbos viram
relacionamentos: consulta, prescreve. O diagrama é a planta baixa
do banco de dados — quanto mais caprichado, mais fácil implementar
depois.
:::

## Fechamento

:::resumo
- DER é a representação conceitual do banco, independente de tecnologia
- Entidades (retângulos), atributos (elipses) e relacionamentos (losangos)
- Cardinalidades: 1:1, 1:N, N:N — indicam quantas ocorrências se relacionam
- Atributos compostos, multivalorados e derivados exigem modelagem especial
- A chave primária conceitual identifica unicamente cada entidade
- Próxima aula: modelagem lógica — transformando DER em tabelas com chaves e normalização
:::
