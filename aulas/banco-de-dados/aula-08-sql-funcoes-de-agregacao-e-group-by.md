# SQL — Funções de agregação e GROUP BY

Consultar registros individuais é apenas o começo. Muitas vezes você precisa de respostas como: quantos alunos estão matriculados? Qual a média de notas da turma? Qual o total de vendas do mês? Para responder perguntas como essas, o SQL oferece as funções de agregação — funções que operam sobre um conjunto de linhas e retornam um único valor resumido.

## Funções de agregação fundamentais

O SQL padrão define cinco funções de agregação principais. Todas elas ignoram valores NULL por padrão (exceto `COUNT(*)`).

:::conceito As cinco funções essenciais
| Função | O que faz | Retorna |
|--------|-----------|---------|
| `COUNT(*)` | Conta o total de linhas | Inteiro |
| `COUNT(coluna)` | Conta linhas com valor não NULL na coluna | Inteiro |
| `SUM(coluna)` | Soma dos valores numéricos | Número |
| `AVG(coluna)` | Média aritmética | Decimal |
| `MAX(coluna)` | Maior valor | Mesmo tipo da coluna |
| `MIN(coluna)` | Menor valor | Mesmo tipo da coluna |
:::

:::exemplo Agregações básicas na tabela alunos
```sql
SELECT COUNT(*) AS total_alunos,
       AVG(EXTRACT(YEAR FROM AGE(data_nascimento))) AS media_idade,
       MAX(data_criacao) AS ultima_matricula
FROM alunos;
```
Uma única consulta que retorna: total de alunos, idade média e data da
matrícula mais recente.
:::

## GROUP BY — agregando por categoria

Sem GROUP BY, as funções de agregação operam sobre TODAS as linhas da tabela. Com GROUP BY, você divide os dados em grupos e aplica a agregação em cada grupo separadamente.

:::importante Regra de ouro do GROUP BY
Toda coluna que aparece no SELECT **sem** estar dentro de uma função de
agregação DEVE aparecer na cláusula GROUP BY. Violar esta regra faz o
banco rejeitar a consulta (no SQL moderno) ou retornar valores
imprevisíveis (no MySQL com sql_mode permissivo).
:::

:::exemplo GROUP BY — matrículas por turma
```sql
SELECT turma_id, COUNT(*) AS total_alunos
FROM matriculas
GROUP BY turma_id
ORDER BY total_alunos DESC;
```
Agrupa matrículas por turma e conta quantas existem em cada uma. A
turma com mais alunos aparece primeiro.
:::

## HAVING — filtrando grupos

O WHERE filtra linhas ANTES da agregação. O HAVING filtra grupos DEPOIS da agregação. Essa diferença é crucial.

:::exemplo WHERE vs HAVING na prática
```sql
-- WHERE filtra antes: só alunos ativos entram no grupo
SELECT turma_id, COUNT(*) AS matriculas_ativas
FROM matriculas
WHERE status = 'ativa'
GROUP BY turma_id;

-- HAVING filtra depois: só grupos com mais de 10 alunos
SELECT turma_id, COUNT(*) AS total
FROM matriculas
GROUP BY turma_id
HAVING COUNT(*) > 10;
```
WHERE restringe quais linhas participam dos grupos. HAVING restringe
quais grupos aparecem no resultado.
:::

:::questao Qual a diferença entre WHERE e HAVING?
a) WHERE filtra depois da agregação, HAVING filtra antes
b) WHERE filtra linhas, HAVING filtra grupos *
c) WHERE e HAVING são intercambiáveis
d) HAVING só funciona com COUNT()
> WHERE filtra linhas individuais antes de qualquer agrupamento. HAVING filtra grupos já agregados.
> É por isso que HAVING pode usar funções como COUNT() ou AVG() na condição — elas só existem depois do agrupamento. WHERE não pode usar funções de agregação.
:::

## Combinando JOIN com GROUP BY

Na prática, GROUP BY quase sempre anda junto com JOIN, já que os dados que você quer agrupar estão em tabelas diferentes.

:::exemplo JOIN + GROUP BY — total de aulas por turma
```sql
SELECT t.nome, COUNT(a.id) AS total_aulas
FROM turmas AS t
LEFT JOIN aulas AS a ON t.id = a.turma_id
GROUP BY t.id, t.nome
ORDER BY total_aulas DESC;
```
LEFT JOIN garante que turmas sem aulas apareçam com total 0 (COUNT de NULL = 0). Se fosse INNER JOIN, turmas vazias seriam omitidas.
:::

:::questao Qual consulta retorna a média de notas por turma, considerando apenas alunos com nota >= 5?
a) SELECT turma_id, AVG(nota) FROM notas WHERE nota >= 5 GROUP BY turma_id *
b) SELECT turma_id, AVG(nota) FROM notas GROUP BY turma_id HAVING nota >= 5
c) SELECT turma_id, AVG(nota) FROM notas HAVING nota >= 5 GROUP BY turma_id
d) SELECT turma_id, AVG(nota) FROM notas WHERE nota >= 5 HAVING turma_id
> A opção A é a correta: WHERE filtra as notas >= 5 antes da agregação, GROUP BY agrupa por turma.
> AVG calcula a média de cada grupo. HAVING com nota >= 5 (opção B) não faz sentido porque HAVING opera sobre grupos, não sobre linhas individuais.
:::

## Fechamento

:::resumo
- Funções de agregação: COUNT, SUM, AVG, MAX, MIN
- GROUP BY: divide os dados em grupos para agregação por categoria
- HAVING: filtra grupos após agregação (diferente de WHERE que filtra linhas)
- Toda coluna não-agregada no SELECT deve estar no GROUP BY
- JOIN + GROUP BY é a combinação mais comum em relatórios
- Próxima aula: subconsultas e views para simplificar consultas complexas
:::
