# SQL — JOINs e consultas multi-tabela

Bancos de dados relacionais não existem no vácuo. Uma das maiores vantagens do modelo relacional é a capacidade de combinar dados de diferentes tabelas em uma única consulta. Até agora você trabalhou com uma tabela por vez, mas na prática raramente uma consulta envolve apenas uma tabela. Nesta aula, você vai aprender a usar os JOINs — a ferramenta central para consultas multi-tabela no SQL.

## O problema dos dados espalhados

Quando um banco é normalizado, os dados ficam distribuídos em várias tabelas. Por exemplo, um pedido está na tabela `pedidos`, os itens do pedido em `itens_pedido`, e os dados do cliente em `clientes`. Para montar uma fatura completa, você precisa trazer dados das três tabelas simultaneamente.

:::importante JOIN não é mágica — é produto cartesiano filtrado
Um JOIN combina duas tabelas gerando um produto cartesiano (cada linha da
tabela A com cada linha da tabela B) e depois filtra pelos pares que
satisfazem a condição de junção. Sem a condição `ON`, o resultado é um
produto cartesiano — quase sempre gigante e sem sentido.
:::

Sem JOINs, você teria que fazer várias consultas e montar o resultado manualmente na aplicação — ineficiente e propenso a erros.

## INNER JOIN — interseção exata

O INNER JOIN retorna apenas as linhas que têm correspondência em ambas as tabelas. É o tipo mais comum de JOIN.

:::exemplo INNER JOIN entre alunos e matrículas
```sql
SELECT alunos.nome, alunos.email, matriculas.turma_id
FROM alunos
INNER JOIN matriculas ON alunos.id = matriculas.aluno_id;
```
Este comando retorna apenas alunos que possuem matrícula. Alunos sem
matrícula não aparecem.
:::

A sintaxe básica é: `tabela_A INNER JOIN tabela_B ON condição`. A condição geralmente compara a chave primária de uma tabela com a chave estrangeira da outra.

:::conceito INNER JOIN visualmente
Pense em dois círculos que se intersectam. O INNER JOIN retorna apenas
a região de interseção — registros que existem nas duas tabelas.
:::

## LEFT JOIN — tabela principal com opcionais

O LEFT JOIN retorna TODAS as linhas da tabela à esquerda, mesmo que não haja correspondência na tabela à direita. Onde não há correspondência, os campos da tabela direita vêm como NULL.

:::exemplo LEFT JOIN — turmas e suas aulas
```sql
SELECT turmas.nome, aulas.titulo, aulas.ordem
FROM turmas
LEFT JOIN aulas ON turmas.id = aulas.turma_id
ORDER BY turmas.nome, aulas.ordem;
```
Turmas sem aulas ainda aparecem no resultado — com `aulas.titulo` como
NULL. Isso é útil para identificar turmas vazias.
:::

:::importante LEFT JOIN vs INNER JOIN na prática
Use INNER JOIN quando você SÓ quer registros que existem nas duas
tabelas. Use LEFT JOIN quando você quer TODOS os registros da esquerda,
com dados da direita se existirem.
:::

## RIGHT JOIN — espelho do LEFT

O RIGHT JOIN é o oposto simétrico: retorna TODAS as linhas da tabela à direita, com ou sem correspondência na esquerda.

:::curiosidade RIGHT JOIN é raro na prática
RIGHT JOIN é o menos usado dos JOINs. A maioria dos desenvolvedores
prefere LEFT JOIN e reorganiza a ordem das tabelas. Isso acontece
porque LEFT JOIN é mais intuitivo (\"tabela principal primeiro\"). O
SQL aceita RIGHT JOIN, mas você raramente vai encontrá-lo em código
profissional.
:::

## FULL JOIN — todo mundo

O FULL JOIN retorna todas as linhas de ambas as tabelas. Quando há correspondência, os dados se combinam. Quando não há, os campos da tabela sem correspondência vêm como NULL.

:::exemplo FULL JOIN — alunos e turmas mesmo sem vínculo
```sql
SELECT alunos.nome, turmas.nome
FROM alunos
FULL JOIN matriculas ON alunos.id = matriculas.aluno_id
FULL JOIN turmas ON matriculas.turma_id = turmas.id;
```
Mostra todos os alunos (mesmo sem matrícula) e todas as turmas (mesmo
vazias). Útil para auditoria de dados órfãos.
:::

## Questões de fixação

:::questao Qual tipo de JOIN retorna apenas os registros que têm correspondência em ambas as tabelas envolvidas?
a) LEFT JOIN
b) FULL JOIN
c) INNER JOIN *
d) CROSS JOIN
> A resposta é INNER JOIN. Ele retorna apenas os registros que possuem correspondência em ambas as tabelas envolvidas no JOIN.
> LEFT JOIN retorna todos os registros da tabela esquerda (mesmo sem correspondência), FULL JOIN retorna todos de ambas as tabelas, e CROSS JOIN retorna o produto cartesiano sem condição de filtro. Cada tipo atende a um cenário diferente.
:::

:::questao Um LEFT JOIN entre a tabela `clientes` (esquerda) e `pedidos` (direita) vai retornar:
a) Apenas clientes que têm pelo menos um pedido
b) Todos os clientes, com dados dos pedidos onde existirem *
c) Todos os pedidos, com dados dos clientes onde existirem
d) A combinação de cada cliente com cada pedido
> LEFT JOIN retorna TODOS os registros da tabela esquerda (clientes), com dados da tabela direita (pedidos) preenchidos onde houver correspondência.
> Clientes sem pedidos aparecem com campos de pedido como NULL. Isso é útil quando você quer ver todos os clientes, independentemente de terem feito pedidos — um relatório de base de clientes, por exemplo.
:::

## Boas práticas com JOINs

:::importante Regras de ouro
1. Sempre use alias (`FROM alunos AS a`) para encurtar o código e
   evitar ambiguidade
2. Especifique a tabela em cada coluna (`a.nome` em vez de só `nome`),
   especialmente em JOINs com colunas de mesmo nome
3. Comece com INNER JOIN e só troque para LEFT se precisar de
   registros sem correspondência
4. Teste com dados pequenos primeiro — um JOIN mal escrito pode
   gerar milhões de linhas sem perceber
5. Use `EXPLAIN ANALYZE` para ver o plano de execução e detectar
   JOINs sem índices
:::

:::exemplo Boas práticas na prática
```sql
-- Ruim: sem alias, sem qualificação
SELECT nome, titulo FROM alunos JOIN matriculas ON id = aluno_id;

-- Bom: alias, colunas qualificadas, legível
SELECT a.nome, m.turma_id
  FROM alunos AS a
  INNER JOIN matriculas AS m ON a.id = m.aluno_id;
```
:::

## Fechamento

:::resumo
- INNER JOIN: só registros com correspondência nos dois lados
- LEFT JOIN: todos da esquerda, dados da direita onde existirem
- RIGHT JOIN: simétrico do LEFT (raro na prática)
- FULL JOIN: todos de ambas as tabelas
- A condição `ON` é o coração do JOIN — sem ela, é produto cartesiano
- Use alias e qualifique colunas sempre
- Próxima aula: funções de agregação (COUNT, SUM, AVG) e GROUP BY
:::
