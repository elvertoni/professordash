# Aula 03 — Modelagem lógica: tabelas, chaves e normalização

Você já sabe criar um DER com entidades, atributos e relacionamentos. Agora vamos transformar esse diagrama conceitual em um esquema lógico — tabelas reais com colunas, tipos de dados, chaves primárias e estrangeiras. E mais: vamos aplicar as regras de normalização para garantir que o banco não tenha dados repetidos ou inconsistentes.

## O que vamos construir

Partindo do DER da biblioteca (aula 02), vamos gerar o esquema lógico completo: tabelas ALUNOS, LIVROS, EMPRESTIMOS com chaves, tipos e normalização até a 3FN.

:::objetivo Resultado final
Esquema lógico textual de 3 tabelas com: nome da tabela, colunas
com tipos, PK, FK e indicação de que está na 3FN.
:::

## Pré-requisitos

:::dica Para esta aula você precisa de
Conceitos de DER, entidades, atributos e cardinalidades da aula 02.
Papel e caneta ou editor de texto. Vontade de pensar em estrutura
de dados.
:::

## Passo a passo

1. **Transformar entidades em tabelas** — Cada entidade do DER vira uma tabela. Cada atributo vira uma coluna.

Do DER da biblioteca, temos as entidades:

```
ALUNO (matricula, nome, email, telefone, data_cadastro)
LIVRO (isbn, titulo, autor, ano_publicacao, quantidade)
EMPRESTIMO (id, data_retirada, data_devolucao, status)
```

```sql
-- Versão inicial (antes da normalização)
CREATE TABLE alunos (
    matricula INTEGER PRIMARY KEY,
    nome TEXT,
    email TEXT,
    telefone TEXT,
    data_cadastro DATE
);
```

2. **Definir chaves primárias** — A chave primária (PK) identifica cada linha unicamente. Pode ser natural (CPF, ISBN) ou substituta (id auto-incrementado).

```sql
CREATE TABLE alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- chave substituta
    matricula TEXT NOT NULL UNIQUE,        -- chave natural alternativa
    nome TEXT NOT NULL
);

CREATE TABLE livros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn TEXT NOT NULL UNIQUE,
    titulo TEXT NOT NULL,
    ano_publicacao INTEGER
);
```

:::conceito Chave primária vs Chave natural vs Chave substituta
Chave natural: existe no mundo real (CPF, ISBN, placa do carro).
Chave substituta (surrogate): criada pelo banco (id auto-incremento).
Vantagem da substituta: nunca muda, é mais rápida, ocupa menos
espaço em chaves estrangeiras. Use sempre id INTEGER PRIMARY KEY
e adicione UNIQUE nas chaves naturais para manter a integridade.
:::

3. **Adicionar chaves estrangeiras** — Relacionamentos 1:N viram FK na tabela do lado N.

```sql
CREATE TABLE emprestimos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER NOT NULL,
    livro_id INTEGER NOT NULL,
    data_retirada DATE NOT NULL,
    data_devolucao DATE,
    status TEXT DEFAULT 'ativo',
    FOREIGN KEY (aluno_id) REFERENCES alunos(id),
    FOREIGN KEY (livro_id) REFERENCES livros(id)
);
```

A tabela EMPRESTIMO é o lado N do relacionamento com ALUNO e LIVRO. Por isso, ela recebe as FKs.

4. **Relacionamento N:N — tabela intermediária** — Se alunos podem pegar vários livros e livros podem ser pegos por vários alunos, precisamos de uma tabela extra.

Mas no nosso modelo, cada empréstimo é de um livro para um aluno (1:N com cada). Se quiséssemos que um empréstimo incluísse vários livros, faríamos:

```sql
CREATE TABLE emprestimo_livros (
    emprestimo_id INTEGER NOT NULL,
    livro_id INTEGER NOT NULL,
    PRIMARY KEY (emprestimo_id, livro_id),
    FOREIGN KEY (emprestimo_id) REFERENCES emprestimos(id),
    FOREIGN KEY (livro_id) REFERENCES livros(id)
);
```

5. **Aplicar a 1ª Forma Normal (1FN)** — Cada coluna deve conter valores atômicos (indivisíveis).

```sql
-- ERRADO: telefones como lista separada por vírgula
CREATE TABLE alunos (
    id INTEGER PRIMARY KEY,
    nome TEXT,
    telefones TEXT  -- "41-99888-0000, 41-91234-5678"
);

-- CERTO: tabela separada para telefones
CREATE TABLE alunos (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL
);

CREATE TABLE telefones (
    id INTEGER PRIMARY KEY,
    aluno_id INTEGER NOT NULL,
    numero TEXT NOT NULL,
    FOREIGN KEY (aluno_id) REFERENCES alunos(id)
);
```

6. **Aplicar a 2ª e 3ª Forma Normal** — 2FN: todo atributo não-chave deve depender da chave completa. 3FN: nenhum atributo não-chave deve depender de outro atributo não-chave.

```sql
-- ERRO (2FN): autor depende do ISBN, não do empréstimo
CREATE TABLE emprestimos (
    id INTEGER PRIMARY KEY,
    livro_isbn TEXT,
    livro_titulo TEXT,
    livro_autor TEXT,  -- depende do livro, não do empréstimo!
    aluno_nome TEXT    -- depende do aluno, não do empréstimo!
);

-- CERTO: cada tabela só tem atributos que dependem da sua própria PK
-- alunos: id, nome, email
-- livros: id, isbn, titulo, autor, ano
-- emprestimos: id, aluno_id, livro_id, data_retirada, data_devolucao
```

:::importante Resumo das 3 formas normais
1FN: colunas atômicas (sem listas ou valores compostos).
2FN: todo atributo depende da chave completa (sem dependência
parcial — relevante para chaves compostas).
3FN: todo atributo depende apenas da chave (sem dependência
transitiva: se A → B e B → C, então C tem que depender de A).
:::

## Checkpoint

:::objetivo Você está no caminho certo se
Seu esquema lógico tem: 3 tabelas (alunos, livros, emprestimos),
cada uma com chave primária explícita, chaves estrangeiras nos
relacionamentos, colunas com tipos definidos, e nenhum dado
repetido desnecessariamente (normalizado até 3FN).
:::

## Erros comuns

:::atencao Sintoma: dados repetidos em várias linhas
Causa: o banco não está normalizado. Exemplo: guardar nome do
aluno na tabela de empréstimos. Correção: se o mesmo dado
aparece em mais de um lugar, ele provavelmente deveria estar
em uma tabela separada referenciada por FK.
:::

:::atencao Sintoma: colunas como telefone1, telefone2, telefone3
Causa: violação da 1FN (atributo multivalorado modelado como
colunas fixas). Correção: crie uma tabela separada TELEFONES
com FK para ALUNOS. Assim o aluno pode ter quantos telefones
precisar sem alterar a estrutura da tabela.
:::

## Desafio

Parta do seguinte DER e transforme em esquema lógico normalizado: CLIENTE (id, nome) ---(1,N)--- PEDIDO (id, data) ---(1,N)--- ITEM_PEDIDO (quantidade, preco_unitario) ---(N,1)--- PRODUTO (id, nome, preco). Escreva as 4 tabelas com CREATE TABLE indicando PK e FK.

:::importante Desafio extra
Para quem terminar primeiro: adicione um índice (INDEX) na coluna
de FK de emprestimos (aluno_id) e explique por que isso melhora
a performance das consultas que buscam empréstimos de um aluno.
:::

## Fechamento

:::resumo
- Entidades viram tabelas; atributos viram colunas
- Chave primária (PK) identifica cada linha unicamente
- Chave estrangeira (FK) conecta tabelas através de referências
- Relacionamento N:N exige tabela intermediária
- 1FN: colunas atômicas; 2FN: dependência total da chave; 3FN: sem dependência transitiva
- Próxima aula: SQL DDL — CREATE, ALTER e DROP na prática
:::
