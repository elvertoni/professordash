# Aula 05 — SQL DML: INSERT, UPDATE e DELETE

Você já criou tabelas com DDL (aula 04). Agora é hora de preenchê-las com dados e manipulá-los. A DML (Data Manipulation Language) é o subconjunto do SQL que lida com os registros propriamente ditos: inserir, atualizar e remover. Nesta aula prática, vamos inserir livros, alunos e empréstimos no banco, atualizar dados e remover registros — sempre com cuidado para não perder dados importantes.

## O que vamos construir

Um script SQL completo que povoa as tabelas da biblioteca (criadas na aula 04) com dados reais, faz atualizações e remoções controladas, usando transações para garantir segurança.

:::objetivo Resultado final
Banco de dados da biblioteca com 5+ autores, 10+ livros, 5+
alunos e 8+ empréstimos. Capacidade de atualizar dados e remover
registros com segurança usando BEGIN/COMMIT/ROLLBACK.
:::

## Pré-requisitos

:::dica Para esta aula você precisa de
SQLite (sqlite3 no terminal) ou MySQL/PostgreSQL. Tabelas criadas
na aula 04 (autores, livros, alunos, emprestimos). Conceitos de
DDL e tipos de dados.
:::

## Passo a passo

1. **Inserir dados com INSERT** — A sintaxe básica para adicionar registros.

```sql
-- Inserir autores
INSERT INTO autores (nome, email, data_nascimento) 
VALUES ('Machado de Assis', 'machado@literatura.com', '1839-06-21');

INSERT INTO autores (nome, email, data_nascimento) 
VALUES ('Clarice Lispector', 'clarice@literatura.com', '1920-12-10');

-- Inserir múltiplos de uma vez
INSERT INTO autores (nome, email) VALUES
    ('J.K. Rowling', 'jk@rowling.com'),
    ('George Orwell', 'orwell@distopia.com'),
    ('Agatha Christie', 'agatha@crime.com');
```

2. **Inserir livros com FK** — Associe cada livro a um autor existente.

```sql
INSERT INTO livros (titulo, autor_id, isbn, ano_publicacao, paginas, disponivel) VALUES
    ('Dom Casmurro', 1, '978-85-01-05473-9', 1899, 256, 1),
    ('A Hora da Estrela', 2, '978-85-01-06521-6', 1977, 88, 1),
    ('Harry Potter e a Pedra Filosofal', 3, '978-85-01-05474-6', 1997, 264, 1),
    ('1984', 4, '978-85-01-05873-7', 1949, 328, 1),
    ('O Assassinato no Expresso Oriente', 5, '978-85-01-06123-2', 1934, 272, 1),
    ('Memórias Póstumas de Brás Cubas', 1, '978-85-01-05011-3', 1881, 240, 1);
```

3. **Consultar para verificar** — Sempre confira se os dados foram inseridos.

```sql
SELECT id, titulo, autor_id FROM livros;
```

4. **Atualizar dados com UPDATE** — Use WHERE para não modificar tudo acidentalmente.

```sql
-- Atualizar email de um autor específico
UPDATE autores 
SET email = 'machado.assis@academia.org'
WHERE id = 1;

-- Marcar livro como indisponível (emprestado)
UPDATE livros 
SET disponivel = 0
WHERE id = 3;

-- Atualizar múltiplos campos de uma vez
UPDATE livros 
SET disponivel = 1, paginas = 272
WHERE id = 5;
```

:::importante CUIDADO: UPDATE sem WHERE
```sql
-- ISSO ATUALIZA TODAS AS LINHAS DA TABELA!
UPDATE livros SET disponivel = 0;

-- Sempre faça SELECT primeiro para ver quais linhas serão afetadas:
SELECT id, titulo FROM livros WHERE id = 3;
-- Depois aplique o UPDATE com o mesmo WHERE:
UPDATE livros SET disponivel = 0 WHERE id = 3;
```
:::

5. **Remover registros com DELETE** — Exclua com responsabilidade.

```sql
-- Remover um livro específico
DELETE FROM livros WHERE id = 6;

-- Remover autores que não têm livros (subconsulta)
DELETE FROM autores 
WHERE id NOT IN (SELECT DISTINCT autor_id FROM livros);
```

:::atencao DELETE vs TRUNCATE vs DROP
DELETE: remove linhas uma a uma, pode ter WHERE, dispara triggers,
pode ser desfeito com ROLLBACK. TRUNCATE: remove todas as linhas
de uma vez, não pode ter WHERE, não dispara triggers, não pode
ser desfeito. DROP: remove a tabela inteira (estrutura + dados).
Regra: use DELETE com WHERE para remoção seletiva, TRUNCATE
para limpar tabela inteira (mais rápido), DROP só se quiser
eliminar a tabela.
:::

6. **Usar transações (BEGIN/COMMIT/ROLLBACK)** — Proteja operações que afetam múltiplas tabelas.

```sql
BEGIN TRANSACTION;

-- Inserir empréstimo
INSERT INTO emprestimos (aluno_id, livro_id, data_retirada, data_devolucao_prevista)
VALUES (1, 3, '2026-05-20', '2026-06-03');

-- Atualizar disponibilidade do livro
UPDATE livros SET disponivel = 0 WHERE id = 3;

-- Se algo der errado até aqui, desfaz tudo:
-- ROLLBACK;

-- Se está tudo certo, confirma:
COMMIT;
```

As transações garantem que ou todas as operações são aplicadas, ou nenhuma. Isso evita que um livro fique marcado como indisponível sem um empréstimo correspondente.

## Checkpoint

:::objetivo Você está no caminho certo se
A tabela autores tem 5 registros, livros tem 6 registros (após
deletar o 6, sobram 5), o email de Machado de Assis foi atualizado,
e o livro Harry Potter está com disponivel=0. Um SELECT * em
cada tabela confirma os dados.
:::

## Erros comuns

:::atencao Sintoma: FOREIGN KEY constraint failed ao inserir
Causa: o autor_id informado não existe na tabela autores.
Correção: primeiro insira o autor, depois o livro. Ou verifique
os IDs dos autores existentes com SELECT id FROM autores.
:::

:::atencao Sintoma: UPDATE ou DELETE não afeta nenhuma linha
Causa: a condição WHERE não encontrou correspondência (erro de
digitação, maiúsculas/minúsculas). Correção: teste o WHERE com
SELECT primeiro para confirmar que as linhas existem.
:::

## Desafio

Crie uma transação que transfere um livro emprestado: insira um novo empréstimo para outro aluno e atualize o empréstimo antigo com a data de devolução real. Tudo dentro de uma única transação.

:::importante Desafio extra
Para quem terminar primeiro: crie um script SQL que insere dados
de teste suficientes para simular uma semana de movimentação na
biblioteca: 10 alunos, 15 livros, 20 empréstimos com datas variadas,
e alguns já devolvidos. Use transações e gere um relatório SELECT
que mostre quantos livros estão emprestados no momento.
:::

## Código completo

```sql
-- ============================================
-- Script completo DML — Biblioteca
-- ============================================

BEGIN TRANSACTION;

-- Autores
INSERT INTO autores (nome, email, data_nascimento) VALUES
    ('Machado de Assis', 'machado@literatura.com', '1839-06-21'),
    ('Clarice Lispector', 'clarice@literatura.com', '1920-12-10'),
    ('J.K. Rowling', 'jk@rowling.com', '1965-07-31'),
    ('George Orwell', 'orwell@distopia.com', '1903-06-25'),
    ('Agatha Christie', 'agatha@crime.com', '1890-09-15');

-- Livros
INSERT INTO livros (titulo, autor_id, isbn, ano_publicacao, paginas, disponivel) VALUES
    ('Dom Casmurro', 1, '978-85-01-05473-9', 1899, 256, 1),
    ('A Hora da Estrela', 2, '978-85-01-06521-6', 1977, 88, 1),
    ('Harry Potter e a Pedra Filosofal', 3, '978-85-01-05474-6', 1997, 264, 1),
    ('1984', 4, '978-85-01-05873-7', 1949, 328, 1),
    ('O Assassinato no Expresso Oriente', 5, '978-85-01-06123-2', 1934, 272, 1);

-- Atualizações
UPDATE autores SET email = 'machado.assis@academia.org' WHERE id = 1;
UPDATE livros SET disponivel = 0 WHERE id = 3;

-- Consultas de verificação
SELECT '--- AUTORES ---' AS info;
SELECT id, nome FROM autores;
SELECT '--- LIVROS ---' AS info;
SELECT id, titulo, disponivel FROM livros;

COMMIT;
```

## Fechamento

:::resumo
- INSERT adiciona registros; pode inserir múltiplos de uma vez
- UPDATE altera registros existentes — SEMPRE com WHERE
- DELETE remove registros — teste com SELECT WHERE primeiro
- Transações (BEGIN/COMMIT/ROLLBACK) agrupam operações atômicas
- FK constraint impede inserir referências a registros inexistentes
- Próxima aula: SQL SELECT, WHERE e ordenação — consultando dados
:::
