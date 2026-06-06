# Aula 04 — SQL DDL: CREATE, ALTER e DROP

Agora que você já entende os conceitos de banco de dados e modelagem, é
hora de colocar a mão no código. DDL (Data Definition Language) é o
subconjunto do SQL responsável por definir e modificar a estrutura do banco:
criar tabelas, alterar colunas e remover objetos. Nesta aula prática, você
vai construir o esquema de um banco de dados para uma biblioteca escolar
usando comandos SQL reais.

## O que vamos construir

O esquema completo de um banco de dados de biblioteca com três tabelas: `livros`, `alunos` e `emprestimos`, incluindo chaves primárias, estrangeiras, constraints e tipos de dados apropriados.

:::objetivo Resultado final
Um arquivo SQL que, executado, cria as tres tabelas com todas as
colunas, tipos adequados, chaves primarias e estrangeiras, e
constraints de unicidade e valor nulo.
:::

## Pré-requisitos

:::dica Para esta aula voce precisa de
Acesso ao SQLite (ja vem instalado no Python — sqlite3 no terminal)
ou ao SQLite Online (https://sqliteonline.com). Conhecer o modelo da
biblioteca que desenhamos na aula anterior.
:::

## Passo a passo

1. **Criar o banco e conectar** — No terminal, digite `sqlite3 biblioteca.db`.

2. **CREATE TABLE — criar a tabela de alunos** — Especifique colunas, tipos e constraints.

```sql
CREATE TABLE alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    telefone TEXT,
    data_cadastro DATE DEFAULT CURRENT_DATE
);
```

3. **CREATE TABLE — criar a tabela de livros** — Inclua colunas com tipos apropriados.

```sql
CREATE TABLE livros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    isbn TEXT UNIQUE,
    ano_publicacao INTEGER,
    quantidade_disponivel INTEGER DEFAULT 1,
    genero TEXT DEFAULT 'Geral'
);
```

:::conceito Tipos de dados no SQL
INTEGER — numeros inteiros. TEXT — textos (strings). REAL — numeros
decimais. DATE — data (AAAA-MM-DD). AUTOINCREMENT — gera automaticamente
um numero unico para cada nova linha.
:::

4. **CREATE TABLE — criar a tabela de empréstimos** — A tabela associativa que conecta alunos e livros.

```sql
CREATE TABLE emprestimos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER NOT NULL,
    livro_id INTEGER NOT NULL,
    data_emprestimo DATE DEFAULT CURRENT_DATE,
    data_devolucao DATE,
    status TEXT DEFAULT 'ativo',
    FOREIGN KEY (aluno_id) REFERENCES alunos(id),
    FOREIGN KEY (livro_id) REFERENCES livros(id)
);
```

5. **ALTER TABLE — modificar uma tabela** — Adicione ou modifique colunas.

```sql
ALTER TABLE livros ADD COLUMN editora TEXT;
ALTER TABLE livros RENAME COLUMN genero TO categoria;
```

6. **DROP TABLE — remover uma tabela** — Cuidado: esta operação é irreversível.

```sql
DROP TABLE IF EXISTS emprestimos;
```

## Checkpoint

:::objetivo Voce esta no caminho certo se
O comando .schema no SQLite exibe as tres tabelas com suas colunas
e constraints. Use .tables para listar as tabelas existentes.
:::

## Erros comuns

:::atencao Sintoma: no such table
Causa: voce esqueceu de criar a tabela antes de referencia-la, ou
fechou e abriu o SQLite sem recriar. Correcao: execute todos os
CREATE TABLE na ordem correta (tabelas sem FK primeiro).
:::

:::atencao Sintoma: FOREIGN KEY constraint failed
Causa: voce tentou inserir um registro com chave estrangeira que
nao existe na tabela referenciada. Correcao: insira primeiro o
registro na tabela pai (alunos, livros) antes de criar o emprestimo.
:::

## Desafio

Adicione uma quarta tabela `categorias` com colunas `id` e `nome`, e modifique a tabela `livros` para referenciar `categorias.id` ao invés do campo texto `genero`.

:::importante Desafio extra
Pesquise sobre ON DELETE CASCADE e recrie a tabela emprestimos
com essa opcao. O que acontece com os emprestimos quando um aluno
e removido? Teste e documente.
:::

## Código completo

```sql
CREATE TABLE alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    telefone TEXT,
    data_cadastro DATE DEFAULT CURRENT_DATE
);
CREATE TABLE livros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    isbn TEXT UNIQUE,
    ano_publicacao INTEGER,
    quantidade_disponivel INTEGER DEFAULT 1,
    genero TEXT DEFAULT 'Geral'
);
CREATE TABLE emprestimos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER NOT NULL,
    livro_id INTEGER NOT NULL,
    data_emprestimo DATE DEFAULT CURRENT_DATE,
    data_devolucao DATE,
    status TEXT DEFAULT 'ativo',
    FOREIGN KEY (aluno_id) REFERENCES alunos(id)
        ON DELETE CASCADE,
    FOREIGN KEY (livro_id) REFERENCES livros(id)
        ON DELETE CASCADE
);
```

## Fechamento

:::resumo
- DDL define a estrutura do banco: CREATE, ALTER, DROP
- CREATE TABLE especifica colunas, tipos e constraints
- PRIMARY KEY identifica cada linha unicamente
- FOREIGN KEY garante integridade referencial entre tabelas
- Proxima aula: manipulando dados com INSERT, UPDATE e DELETE
:::
