# Projeto final — Modelagem de sistema escolar

Você aprendeu modelagem conceitual, SQL DDL, DML, JOINs, subconsultas, views, índices e triggers. Agora chegou o momento de integrar tudo em um projeto completo: modelar e implementar o banco de dados de um sistema escolar do zero — do diagrama entidade-relacionamento ao SQL funcional.

## O problema

A Escola Estadual ProfessorDash precisa de um sistema para gerenciar alunos, turmas, professores e atividades escolares. Atualmente tudo é controlado em planilhas e papéis. O diretor pediu um banco de dados relacional que atenda aos seguintes requisitos:

:::objetivo Requisitos do sistema
1. Cadastro de alunos com dados pessoais e contato
2. Cadastro de professores com especialidade e carga horária
3. Turmas com ano letivo, turno e professor responsável
4. Matrícula de alunos em turmas (um aluno pode estar em várias turmas)
5. Disciplinas com carga horária mínima
6. Alocação de disciplinas em turmas com professor designado
7. Registro de notas por aluno/disciplina/turma/bimestre
8. Controle de frequência por aula
9. Histórico de todas as alterações em notas (auditoria)
:::

## Fase 1 — Modelagem conceitual (DER)

Antes de escrever qualquer SQL, modele as entidades e seus relacionamentos.

:::conceito Entidades identificadas
- **Aluno:** id, nome, data_nascimento, email, telefone, data_matricula
- **Professor:** id, nome, email, especialidade, carga_horaria
- **Turma:** id, codigo, ano_letivo, turno, professor_responsavel (FK)
- **Disciplina:** id, nome, carga_horaria_minima
- **Matricula:** aluno (FK), turma (FK), data_matricula, status
- **AlocacaoDisciplina:** turma (FK), disciplina (FK), professor (FK)
- **Avaliacao:** id, alocacao (FK), bimestre, descricao, peso
- **Nota:** avaliacao (FK), aluno (FK), valor
- **Frequencia:** id, alocacao (FK), aluno (FK), data, presente (boolean)
- **LogNota:** id, nota (FK), valor_antigo, valor_novo, usuario, data_hora
:::

## Fase 2 — SQL DDL

Transforme o DER em tabelas SQL com chaves, constraints e índices.

:::exemplo Script de criação
```sql
-- Tabelas base
CREATE TABLE alunos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    data_nascimento DATE NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    telefone VARCHAR(20),
    data_matricula TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE professores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    especialidade VARCHAR(100),
    carga_horaria INTEGER CHECK (carga_horaria > 0 AND carga_horaria <= 40)
);

CREATE TABLE turmas (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    ano_letivo INTEGER NOT NULL CHECK (ano_letivo >= 2024),
    turno VARCHAR(10) CHECK (turno IN ('matutino', 'vespertino', 'noturno')),
    professor_responsavel INTEGER REFERENCES professores(id)
);

-- Tabelas de relacionamento
CREATE TABLE matriculas (
    aluno_id INTEGER REFERENCES alunos(id) ON DELETE CASCADE,
    turma_id INTEGER REFERENCES turmas(id) ON DELETE RESTRICT,
    data_matricula DATE DEFAULT CURRENT_DATE,
    status VARCHAR(10) DEFAULT 'ativa' CHECK (status IN ('ativa', 'trancada', 'concluida')),
    PRIMARY KEY (aluno_id, turma_id)
);

CREATE TABLE alocacao_disciplinas (
    id SERIAL PRIMARY KEY,
    turma_id INTEGER REFERENCES turmas(id) ON DELETE CASCADE,
    disciplina_id INTEGER REFERENCES disciplinas(id) ON DELETE RESTRICT,
    professor_id INTEGER REFERENCES professores(id) ON DELETE SET NULL,
    UNIQUE (turma_id, disciplina_id)
);
```
:::

## Fase 3 — Índices e performance

Identifique as colunas mais consultadas e crie índices estratégicos.

:::exemplo Índices recomendados
```sql
-- Busca de alunos por email (login)
CREATE INDEX idx_alunos_email ON alunos(email);

-- Notas por avaliação (boletim)
CREATE INDEX idx_notas_avaliacao ON notas(avaliacao_id);

-- Frequência por alocação (chamada)
CREATE INDEX idx_frequencia_alocacao ON frequencias(alocacao_id, data);

-- Histórico por nota (auditoria)
CREATE INDEX idx_log_nota ON log_notas(nota_id, data_hora DESC);
```
:::

## Fase 4 — Trigger de auditoria

Implemente um trigger que registre automaticamente qualquer alteração em notas.

:::exemplo Trigger de auditoria
```sql
CREATE OR REPLACE FUNCTION auditar_nota()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND OLD.valor IS DISTINCT FROM NEW.valor THEN
        INSERT INTO log_notas(nota_id, valor_antigo, valor_novo, operacao, usuario)
        VALUES (OLD.id, OLD.valor, NEW.valor, 'UPDATE', current_user);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_auditar_nota
    AFTER UPDATE ON notas
    FOR EACH ROW
    EXECUTE FUNCTION auditar_nota();
```
:::

## Questões de fixação

:::questao Por que a tabela `matriculas` usa uma chave primária composta por (aluno_id, turma_id) em vez de um id auto-incremento?
a) Porque chaves compostas são mais rápidas
b) Porque um aluno não pode se matricular duas vezes na mesma turma *
c) Porque não é possível usar SERIAL em tabelas de relacionamento
d) Porque chaves compostas ocupam menos espaço
> A chave primária composta (aluno_id, turma_id) garante que cada par aluno-turma é único.
> Um id serial permitiria múltiplas matrículas do mesmo aluno na mesma turma, o que não faz sentido no mundo real.
:::

:::questao Qual o efeito de ON DELETE SET NULL na tabela `alocacao_disciplinas` para a coluna `professor_id`?
a) A alocação é excluída quando o professor sai
d) O professor_id fica NULL quando o professor é removido, mas a alocação permanece *
b) A exclusão do professor é impedida
c) Um professor default é atribuído automaticamente
> SET NULL preserva a alocação da disciplina na turma mesmo que o professor seja removido — a turma fica sem professor designado.
> Se usássemos CASCADE, a alocação inteira sumiria e o histórico de avaliações ficaria órfão.
:::

## Fechamento

:::resumo
- Projeto completo de banco de dados: DER → DDL → índices → triggers
- 10 entidades modeladas com relacionamentos e constraints
- Chaves estrangeiras com ações apropriadas (CASCADE, RESTRICT, SET NULL)
- Índices estratégicos para consultas frequentes
- Trigger de auditoria para rastrear alterações em notas
- CHECK constraints garantem dados válidos (turno, status, carga horária)
- Este projeto serve como template para modelagem de sistemas reais
:::
