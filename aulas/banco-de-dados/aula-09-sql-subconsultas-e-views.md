# SQL — Subconsultas e views

Nem toda consulta pode ser resolvida com um único SELECT. Às vezes você precisa usar o resultado de uma consulta como entrada para outra. É aí que entram as subconsultas — consultas aninhadas dentro de outras consultas. Já as views permitem salvar consultas como se fossem tabelas virtuais, simplificando o acesso a dados complexos.

## Subconsultas no WHERE

O uso mais direto de subconsultas é filtrar com base no resultado de outra consulta. A subconsulta roda primeiro, e seu resultado alimenta a consulta externa.

:::exemplo Subconsulta com IN
```sql
SELECT nome, email
FROM alunos
WHERE id IN (
    SELECT aluno_id
    FROM matriculas
    WHERE turma_id = 1
);
```
A subconsulta interna encontra todos os `aluno_id` matriculados na
turma 1. A consulta externa busca os dados completos desses alunos.
:::

:::importante Performance de subconsultas
Subconsultas com IN podem ser lentas em tabelas grandes. Muitos bancos
de dados otimizam IN para JOIN automaticamente, mas quando a
performance é crítica, prefira INNER JOIN explícito. Use EXPLAIN para
verificar o plano de execução.
:::

## Subconsultas no SELECT

Subconsultas também podem aparecer na lista de colunas do SELECT, funcionando como colunas calculadas.

:::exemplo Subconsulta como coluna calculada
```sql
SELECT a.nome AS aluno,
       (SELECT COUNT(*) FROM entregas e
        WHERE e.aluno_id = a.id AND e.status = 'aprovada') AS entregas_aprovadas
FROM alunos a
ORDER BY entregas_aprovadas DESC;
```
Para cada aluno, a subconsulta conta quantas entregas foram aprovadas
— tudo em uma única consulta.
:::

## Subconsultas correlacionadas

Uma subconsulta é correlacionada quando faz referência a colunas da consulta externa. Ela precisa ser reavaliada para cada linha da consulta externa.

:::exemplo Subconsulta correlacionada
```sql
SELECT a.titulo, a.data_criacao
FROM aulas a
WHERE a.data_criacao = (
    SELECT MAX(a2.data_criacao)
    FROM aulas a2
    WHERE a2.turma_id = a.turma_id
);
```
Para cada turma (referência `a.turma_id`), encontra a aula mais
recente. A subconsulta é reavaliada para cada aula, uma por vez.
:::

## Views — tabelas virtuais

Uma VIEW é uma consulta salva que se comporta como uma tabela. Você pode fazer SELECT em uma view como se fosse uma tabela real, mas os dados não são armazenados — são calculados sob demanda.

:::exemplo Criando e usando uma view
```sql
CREATE VIEW resumo_turma AS
SELECT t.nome AS turma,
       COUNT(DISTINCT m.aluno_id) AS total_alunos,
       COUNT(DISTINCT a.id) AS total_aulas,
       COUNT(DISTINCT atv.id) AS total_atividades
FROM turmas t
LEFT JOIN matriculas m ON t.id = m.turma_id
LEFT JOIN aulas a ON t.id = a.turma_id
LEFT JOIN atividades atv ON t.id = atv.turma_id
GROUP BY t.id, t.nome;

-- Usar a view é como consultar uma tabela:
SELECT * FROM resumo_turma WHERE total_alunos > 10;
```
:::

:::conceito Vantagens das views
1. **Segurança:** conceda acesso a uma view sem expor tabelas sensíveis
2. **Simplicidade:** consultas complexas viram SELECT simples
3. **Consistência:** todos usam a mesma lógica de negócio
4. **Manutenibilidade:** mude a view, não as consultas espalhadas
:::

## Questões de fixação

:::questao Qual a diferença entre uma subconsulta e um JOIN?
a) Subconsultas são sempre mais rápidas que JOINs
b) JOINs combinam tabelas no mesmo nível; subconsultas aninham resultados *
c) Subconsultas só funcionam no WHERE
d) Não há diferença prática
> JOINs combinam linhas de duas tabelas no mesmo nível. Subconsultas passam o resultado de uma consulta como entrada para outra.
> Subconsultas podem estar no WHERE (filtrando resultados), SELECT (coluna calculada), FROM (tabela virtual) ou HAVING. Cada posição tem um uso específico e cabe em cenários diferentes.
:::

:::questao Quando uma view é atualizada automaticamente?
a) A cada minuto pelo banco
c) Sempre que é consultada (os dados são calculados na hora) *
b) Quando o criador da view executa REFRESH
d) Views não podem ser atualizadas
> Views são consultas salvas, não dados armazenados. Cada SELECT em uma view executa a consulta subjacente em tempo real.
> Os dados refletem sempre o estado atual do banco, diferente de uma tabela temporária que precisa ser recriada manualmente.
:::

## Fechamento

:::resumo
- Subconsultas no WHERE: filtram resultados com IN, EXISTS, NOT IN
- Subconsultas no SELECT: colunas calculadas por linha
- Subconsultas correlacionadas: referenciam colunas externas, são reavaliadas por linha
- Views: consultas salvas que funcionam como tabelas virtuais
- Views simplificam segurança, consistência e manutenção
- Próxima aula: índices, performance e otimização de consultas
:::
