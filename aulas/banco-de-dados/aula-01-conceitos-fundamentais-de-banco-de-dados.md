# Aula 01 — Conceitos fundamentais de banco de dados

Você usa bancos de dados todos os dias sem perceber. Quando curte uma foto
no Instagram, pesquisa um produto no Mercado Livre ou confere seu boletim
escolar, há um banco de dados trabalhando nos bastidores. Nesta aula, vamos
entender o que é um banco de dados, como os dados são organizados no modelo
relacional e qual o papel do SGBD (Sistema Gerenciador de Banco de Dados)
nessa história.

## O que é um banco de dados?

Um banco de dados é uma coleção organizada de dados armazenados eletronicamente. Diferente de uma planilha ou arquivo de texto, um banco de dados oferece mecanismos para armazenar, consultar, atualizar e proteger informações de forma eficiente e segura.

:::conceito Banco de Dados
Conjunto estruturado de dados que representa informacoes do mundo real
e pode ser acessado, manipulado e gerenciado por um SGBD. Nao e apenas
um arquivo — e um sistema com regras, relacionamentos e garantias de
consistencia.
:::

## Dado, informação e conhecimento

É importante distinguir esses três conceitos que estão no centro da disciplina.

:::importante Dado vs Informacao vs Conhecimento
Dado e um fato bruto: "950" ou "Maria". Informacao e o dado com
contexto: "Maria tirou 950 no ENEM". Conhecimento e a informacao
aplicada para tomar decisao: "Maria pode entrar em universidades
publicas com essa nota". Um banco de dados armazena dados e os
transforma em informacao atraves de consultas.
:::

## Modelo relacional

Criado por Edgar Codd em 1970, o modelo relacional organiza dados em tabelas (relações) compostas por linhas (tuplas/registros) e colunas (atributos/campos).

:::exemplo Tabelas relacionadas na biblioteca
Tabela ALUNOS:
| id (PK) | nome   | turma_id (FK) |
|---------|--------|---------------|
| 1       | Ana    | 1             |
| 2       | Bruno  | 1             |
| 3       | Carla  | 2             |
Tabela TURMAS:
| id (PK) | nome                  |
|---------|-----------------------|
| 1       | Programacao Front-End |
| 2       | Programacao Back-End  |
A coluna turma_id em ALUNOS e a chave estrangeira que liga cada aluno
a sua turma.
:::

## SGBD e SQL

Um SGBD (Sistema Gerenciador de Banco de Dados) é o software responsável por criar, manter e proteger bancos de dados. SQL (Structured Query Language) é a linguagem padrão para se comunicar com bancos relacionais.

:::curiosidade O banco mais usado na web
O MySQL e um dos SGBDs mais populares do mundo, usado por empresas
como Facebook, Twitter e YouTube. O PostgreSQL e preferido por sua
conformidade com padroes SQL e recursos avancados. O ProfessorDash
usa PostgreSQL em producao e SQLite em desenvolvimento.
:::

A SQL se divide em subconjuntos: DDL (CREATE, ALTER, DROP) para definir estrutura; DML (INSERT, UPDATE, DELETE) para manipular dados; DQL (SELECT) para consultar dados; e DCL (GRANT, REVOKE) para controlar permissões.

## Questões de fixação

:::questao Em um banco de dados relacional, o que e uma chave estrangeira (foreign key)?
a) Uma coluna que identifica unicamente cada linha da tabela
b) Uma coluna que referencia a chave primaria de outra tabela *
c) Uma chave que permite acesso remoto ao banco de dados
d) Um indice criado automaticamente para acelerar consultas
> A chave estrangeira (FK) e uma coluna em uma tabela que referencia a
> chave primaria de outra tabela. Ela estabelece o relacionamento entre
> as tabelas e garante a integridade referencial. A chave primaria (PK)
> e que identifica unicamente cada linha.
:::

:::questao Qual das alternativas NAO e uma caracteristica de um SGBD?
a) Garantir a consistencia dos dados atraves de regras de integridade
b) Permitir que multiplos usuarios acessem os dados simultaneamente
c) Substituir completamente o sistema operacional do computador *
d) Fornecer mecanismos de backup e recuperacao de dados
> Um SGBD e um software que roda sobre o sistema operacional — ele nao
> substitui o SO em nenhuma circunstancia. Suas funcoes reais incluem
> controle de concorrencia, integridade referencial, seguranca e backup.
> O sistema operacional continua responsavel pelo gerenciamento de hardware.
:::

## Atividade prática

Pense em um sistema de biblioteca escolar. Identifique quais tabelas seriam necessárias, quais colunas cada uma teria e como elas se relacionariam.

:::objetivo Entrega
Crie um diagrama textual (no papel ou digitado) com as principais
tabelas de uma biblioteca: LIVROS, ALUNOS, EMPRESTIMOS. Indique as
chaves primarias e estrangeiras em cada uma. Entregue como arquivo
biblioteca-modelo.txt ou foto do caderno.
:::

:::roteiro
Pessoal, pensem no sistema da biblioteca da escola. Quando um aluno
pega um livro emprestado, que informacoes sao registradas? O livro,
o aluno, a data de retirada e devolucao. Isso da tres tabelas bem
claras. O emprestimo e a tabela que conecta as outras duas.
:::

## Fechamento

:::resumo
- Banco de dados e uma colecao organizada de dados gerenciada por SGBD
- Modelo relacional organiza dados em tabelas com linhas e colunas
- Chave primaria identifica cada linha unicamente
- Chave estrangeira conecta tabelas atraves de referencias
- Proxima aula: modelagem conceitual com diagramas entidade-relacionamento
:::
