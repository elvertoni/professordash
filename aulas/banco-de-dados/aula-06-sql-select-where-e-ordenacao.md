# Aula 06 — SQL SELECT, WHERE e ordenação

Criar tabelas e inserir dados é apenas metade do trabalho. A parte mais
importante — e mais frequente — é consultar os dados. O comando SELECT é
a ferramenta mais poderosa do SQL, permitindo buscar, filtrar, ordenar e
transformar informações de formas quase infinitas. Nesta aula prática, você
vai dominar SELECT com WHERE, ORDER BY e LIMIT, usando o banco da biblioteca
que criamos na aula anterior.

## O que vamos construir

Um conjunto de consultas SQL que extraem informações da biblioteca: listar livros disponíveis, verificar quais alunos têm empréstimos ativos, ordenar por data e filtrar por categoria.

:::objetivo Resultado final
Consultas SQL que retornam: (1) todos os livros ordenados por titulo,
(2) livros de uma categoria especifica, (3) alunos com emprestimos em
atraso, (4) os 3 livros mais recentes cadastrados.
:::

## Pré-requisitos

:::dica Para esta aula voce precisa de
O banco biblioteca.db com as tabelas alunos, livros e emprestimos
criadas na aula anterior, e alguns registros inseridos. Se nao tiver,
use os comandos INSERT abaixo para popular o banco.
:::

```sql
INSERT INTO alunos (nome, email) VALUES
    ('Ana Silva', 'ana@escola.com'),
    ('Bruno Costa', 'bruno@escola.com'),
    ('Carla Souza', 'carla@escola.com');
INSERT INTO livros (titulo, autor, genero) VALUES
    ('Dom Casmurro', 'Machado de Assis', 'Romance'),
    ('1984', 'George Orwell', 'Ficcao'),
    ('O Pequeno Principe', 'Antoine Saint-Exupery', 'Infantil'),
    ('Senhor dos Aneis', 'J.R.R. Tolkien', 'Fantasia'),
    ('Python para Data Science', 'Joao Dados', 'Tecnico');
INSERT INTO emprestimos (aluno_id, livro_id, data_emprestimo) VALUES
    (1, 1, '2026-03-01'),
    (2, 3, '2026-03-10'),
    (3, 5, '2026-02-20');
```

## Passo a passo

1. **SELECT básico** — Retorna colunas de uma tabela.

```sql
SELECT * FROM livros;
SELECT titulo, autor FROM livros;
```

:::conceito SELECT versus colunas especificas
SELECT * e pratico para explorar, mas em producao e melhor listar
as colunas desejadas. Isso torna a consulta mais eficiente e evita
surpresas se a estrutura da tabela mudar.
:::

2. **WHERE — filtrando resultados** — WHERE é a cláusula de filtro.

```sql
SELECT titulo, autor FROM livros WHERE genero = 'Fantasia';
SELECT titulo FROM livros WHERE genero != 'Tecnico';
SELECT titulo FROM livros WHERE titulo LIKE '%Python%';
```

3. **Operadores lógicos: AND, OR e NOT** — Combine condições.

```sql
SELECT titulo FROM livros WHERE genero = 'Romance' AND autor LIKE '%Machado%';
SELECT titulo FROM livros WHERE genero = 'Fantasia' OR genero = 'Ficcao';
SELECT titulo FROM livros WHERE NOT genero = 'Infantil';
```

4. **ORDER BY — ordenando resultados** — ASC para crescente (padrão), DESC para decrescente.

```sql
SELECT titulo, autor FROM livros ORDER BY titulo;
SELECT titulo, ano_publicacao FROM livros ORDER BY ano_publicacao DESC;
SELECT autor, titulo FROM livros ORDER BY autor ASC, titulo ASC;
```

5. **LIMIT e OFFSET — limitando resultados** — Útil para amostras e paginação.

```sql
SELECT * FROM livros ORDER BY titulo LIMIT 3;
SELECT * FROM livros ORDER BY titulo LIMIT 3 OFFSET 2;
```

## Checkpoint

:::objetivo Voce esta no caminho certo se
Cada consulta SQL retorna os resultados esperados. SELECT * FROM livros
WHERE genero = 'Fantasia' retorna 1 linha (Senhor dos Aneis). SELECT
count(*) FROM emprestimos WHERE data_devolucao IS NULL retorna 3.
:::

## Erros comuns

:::atencao Sintoma: no such column
Causa: voce escreveu o nome da coluna errado ou com acento. Correcao:
use .schema livros para ver os nomes exatos das colunas. No SQL, nomes
nao tem acentos nem cedilha.
:::

:::atencao Sintoma: consulta retorna vazia mas os dados existem
Causa: erro de digitacao no valor do filtro ou uso de maiusculas/
minusculas incorreto. Correcao: SQLite e case-insensitive para texto,
mas use LIKE com % para buscas flexiveis.
:::

## Desafio

Crie uma consulta que mostre quantos livros cada gênero tem (use `COUNT(*)` e `GROUP BY`). Depois, mostre apenas os gêneros com mais de 1 livro (use `HAVING`).

:::importante Desafio extra
Crie uma consulta que liste o nome do aluno, o titulo do livro e a
data do emprestimo de todos os emprestimos ativos, ordenados do mais
antigo para o mais recente. Dica: isso vai usar JOIN.
:::

## Código completo

```sql
-- 1. Todos os livros ordenados por titulo
SELECT titulo, autor, genero FROM livros ORDER BY titulo;

-- 2. Livros de uma categoria especifica
SELECT titulo, autor FROM livros WHERE genero = 'Romance';

-- 3. Livros com "Python" no titulo
SELECT * FROM livros WHERE titulo LIKE '%Python%';

-- 4. Alunos ordenados por nome (decrescente)
SELECT nome, email FROM alunos ORDER BY nome DESC;

-- 5. Emprestimos ativos
SELECT * FROM emprestimos WHERE status = 'ativo';

-- 6. Emprestimos de marco/2026
SELECT * FROM emprestimos
WHERE data_emprestimo >= '2026-03-01' AND data_emprestimo < '2026-04-01';

-- 7. Os 3 primeiros alunos cadastrados
SELECT * FROM alunos ORDER BY id LIMIT 3;

-- 8. Livros que NAO sao do genero Infantil
SELECT titulo, genero FROM livros WHERE NOT genero = 'Infantil' ORDER BY genero;
```

## Fechamento

:::resumo
- SELECT projeta colunas; WHERE filtra linhas
- Operadores: =, !=, LIKE, BETWEEN, IN
- Logicos: AND, OR, NOT combinam condicoes
- ORDER BY ordena; LIMIT + OFFSET paginam resultados
- Proxima aula: consultas multi-tabela com JOINs
:::
