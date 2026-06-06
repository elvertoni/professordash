# Índices, performance e boas práticas

Quando um banco de dados cresce, consultas que antes eram instantâneas começam a demorar segundos — ou minutos. O principal motivo? O banco está varrendo a tabela inteira para encontrar os dados. A solução mais comum é o índice: uma estrutura auxiliar que acelera a busca, como o índice remissivo no final de um livro.

## Como o banco busca dados sem índice

Sem índice, o banco faz uma varredura sequencial (sequential scan ou full table scan): ele lê cada linha da tabela do começo ao fim, comparando o valor procurado. Numa tabela de 10 linhas é instantâneo. Numa de 10 milhões, é catastrófico.

:::conceito Custo de uma varredura sequencial
```
Tabela: 10.000.000 linhas
Operação: SELECT * FROM alunos WHERE email = 'joao@escola.pr.gov.br'
Custo sem índice: ler 10.000.000 linhas (full scan)
Custo com índice: ler ~3-5 páginas do índice + 1 página da tabela
Ganho: ~1.000.000x mais rápido
```
:::

## Como os índices funcionam

Um índice é uma estrutura de dados separada (normalmente uma B-tree) que armazena os valores de uma ou mais colunas em ordem, junto com ponteiros para as linhas correspondentes na tabela.

:::exemplo Criando e usando um índice
```sql
-- Criar índice na coluna mais buscada
CREATE INDEX idx_alunos_email ON alunos(email);

-- O banco usa o índice automaticamente quando a consulta filtra por email
SELECT * FROM alunos WHERE email = 'maria@escola.pr.gov.br';

-- Verificar o plano de execução
EXPLAIN ANALYZE SELECT * FROM alunos WHERE email = 'maria@escola.pr.gov.br';
```
:::

:::importante Índices não são mágica gratuita
- Índices aceleram SELECT, mas lentificam INSERT, UPDATE e DELETE
  (precisam ser atualizados a cada modificação)
- Índices ocupam espaço em disco
- Índices em colunas com poucos valores distintos (ex.: sexo, status
  com 2-3 valores) têm baixo benefício
- Muitos índices podem piorar a performance geral do banco
:::

## Tipos de índice

Cada banco oferece tipos diferentes de índice para cenários diferentes.

:::conceito Principais tipos

- **B-tree:** Busca por igualdade e intervalo (padrão). Ex: `WHERE id = 5`
- **Hash:** Busca por igualdade exata. Ex: `WHERE email = \'x@y.com\'`
- **GiST:** Dados geoespaciais e texto completo
- **GIN:** Arrays e JSONB
- **BRIN:** Colunas ordenadas em tabelas grandes. Ex: datas
:::

## Índices compostos

Um índice pode cobrir múltiplas colunas. A ordem das colunas importa — o banco usa o índice da esquerda para a direita.

:::exemplo Índice composto na prática
```sql
-- Índice em (turma_id, status)
CREATE INDEX idx_matriculas_turma_status ON matriculas(turma_id, status);

-- Usa o índice completamente:
SELECT * FROM matriculas WHERE turma_id = 1 AND status = 'ativa';

-- Usa o índice parcialmente (só a primeira coluna):
SELECT * FROM matriculas WHERE turma_id = 1;

-- NÃO usa o índice (pula a primeira coluna):
SELECT * FROM matriculas WHERE status = 'ativa';
```
:::

## Boas práticas de performance

:::importante Checklist de performance
1. **Sempre use EXPLAIN ANALYZE** antes de otimizar — não adivinhe
2. **Crie índices para colunas usadas em WHERE, JOIN e ORDER BY**
3. **Evite índices em colunas com baixa cardinalidade** (poucos valores
   únicos como 'sim'/'não')
4. **Prefira índices compostos a vários índices simples** quando as
   colunas são consultadas juntas
5. **Monitore índices não usados** — `pg_stat_user_indexes` no PostgreSQL
6. **Faça manutenção periódica:** REINDEX e VACUUM (PostgreSQL),
   OPTIMIZE TABLE (MySQL)
:::

## Questões de fixação

:::questao O que acontece quando você cria um índice em uma coluna que tem apenas 2 valores distintos (ex.: ativo/inativo)?
a) A performance melhora drasticamente
b) O índice ocupa espaço e quase não acelera as buscas *
c) O banco recusa criar o índice
d) A tabela para de aceitar inserts
> Índices em colunas com baixa cardinalidade são ineficientes.
> Com apenas 2 valores distintos, o índice aponta para ~50% das linhas — o banco avalia que é mais rápido varrer a tabela inteira.
:::

:::questao Qual ferramenta do SQL mostra como o banco planeja executar uma consulta?
a) SHOW PLAN
b) DESCRIBE QUERY
c) EXPLAIN *
d) PROFILE
> EXPLAIN mostra o plano de execução que o banco escolheu — se usa índices, tipo de JOIN, estimativa de linhas.
> EXPLAIN ANALYZE executa a consulta de fato e mostra os números reais (tempo, linhas em cada etapa).
:::

## Fechamento

:::resumo
- Full table scan: ler toda a tabela — aceitável em tabelas pequenas, catastrófico em grandes
- Índices: estruturas auxiliares que aceleram buscas (como um índice remissivo)
- Tipos: B-tree (padrão), Hash, GiST, GIN, BRIN
- Índices compostos: ordem das colunas importa
- Trade-off: SELECT mais rápido, INSERT/UPDATE mais lentos
- Sempre meça com EXPLAIN antes de otimizar
- Próxima aula: integridade referencial e triggers
:::
