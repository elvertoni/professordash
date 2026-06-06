# Integridade referencial e triggers

Manter a consistência dos dados é uma das responsabilidades mais importantes de um banco de dados relacional. Se um aluno é removido, o que acontece com suas matrículas? Se uma turma é excluída, as aulas dela devem sumir também? O SQL oferece duas ferramentas poderosas para automatizar essas regras: integridade referencial (via chaves estrangeiras) e triggers (gatilhos que disparam automaticamente).

## Integridade referencial com chaves estrangeiras

Uma chave estrangeira (FOREIGN KEY) é uma restrição que garante que um valor em uma coluna existe como chave primária em outra tabela. Ela impede dados órfãos — registros que referenciam algo que não existe mais.

:::exemplo Criando chave estrangeira
```sql
CREATE TABLE matriculas (
    id SERIAL PRIMARY KEY,
    aluno_id INTEGER NOT NULL,
    turma_id INTEGER NOT NULL,
    data_matricula DATE DEFAULT CURRENT_DATE,
    CONSTRAINT fk_matriculas_aluno
        FOREIGN KEY (aluno_id) REFERENCES alunos(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_matriculas_turma
        FOREIGN KEY (turma_id) REFERENCES turmas(id)
        ON DELETE RESTRICT
);
```
:::

## Ações de integridade referencial

Quando um registro referenciado é deletado ou atualizado, você define o que acontece com os registros que dependem dele.

:::conceito Ações ON DELETE e ON UPDATE
| Ação | Comportamento |
|------|---------------|
| `CASCADE` | Propaga a exclusão/atualização para os registros dependentes |
| `RESTRICT` | Impede a exclusão se existirem dependentes |
| `SET NULL` | Define a chave estrangeira como NULL |
| `SET DEFAULT` | Define a chave para o valor padrão |
| `NO ACTION` | Similar a RESTRICT, mas verificada no final da transação |
:::

:::importante Escolha a ação certa para cada caso
- **CASCADE:** relações de dependência forte (aula pertence a turma →
  se turma for excluída, as aulas devem sumir)
- **RESTRICT:** proteção contra exclusão acidental (não deixe excluir
  um aluno que tem entregas)
- **SET NULL:** relação opcional (se o professor for removido, a turma
  pode ficar sem professor designado)
:::

## Triggers — automação no banco

Um trigger é uma função que executa automaticamente quando ocorre um evento na tabela (INSERT, UPDATE, DELETE). Diferente das constraints que apenas validam, triggers podem executar lógica arbitrária.

:::exemplo Trigger que registra auditoria
```sql
-- Função que será chamada pelo trigger
CREATE OR REPLACE FUNCTION auditar_exclusao()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO log_operacoes(tabela, registro_id, operacao, usuario)
    VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', current_user);
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Trigger que executa antes de deletar qualquer aula
CREATE TRIGGER trg_auditar_exclusao_aula
    BEFORE DELETE ON aulas
    FOR EACH ROW
    EXECUTE FUNCTION auditar_exclusao();
```
:::

## Trigger vs constraint — quando usar cada um

:::conceito Comparação
| Cenário | Solução |
|---------|---------|
| Impedir exclusão de aluno com entregas | FOREIGN KEY com RESTRICT |
| Deletar matrículas ao excluir aluno | FOREIGN KEY com CASCADE |
| Registrar quem modificou um registro | Trigger BEFORE UPDATE |
| Atualizar data da última modificação | Trigger BEFORE UPDATE |
| Validar formato de email | CHECK constraint (ou trigger se precisar de regex complexo) |
| Sincronizar tabela de resumo | Trigger AFTER INSERT/UPDATE/DELETE |
:::

## Questões de fixação

:::questao O que acontece com as matrículas de um aluno quando o aluno é excluído do banco, se a chave estrangeira foi definida com ON DELETE CASCADE?
a) As matrículas ficam órfãs com aluno_id = NULL
b) As matrículas são automaticamente excluídas junto com o aluno *
c) A exclusão do aluno é impedida
d) As matrículas são movidas para uma tabela de backup
> CASCADE propaga a exclusão: quando o registro pai é removido, todos os registros filhos que referenciam ele via chave estrangeira também são removidos.
> Isso é útil quando a existência do filho depende totalmente do pai (ex.: matrículas de um aluno). Mas cuidado: CASCADE em excesso pode deletar mais dados do que você espera.
:::

:::questao Qual a diferença entre um trigger BEFORE DELETE e AFTER DELETE?
a) BEFORE DELETE executa antes da exclusão; AFTER DELETE depois *
b) BEFORE DELETE executa depois; AFTER DELETE antes
c) Não há diferença — ambos executam no mesmo momento
d) BEFORE DELETE só funciona com INSERT
> BEFORE DELETE roda antes da exclusão efetiva — usado para registrar o valor antigo em log de auditoria ou validar regras de negócio.
> AFTER DELETE roda depois da exclusão — útil para atualizar tabelas de resumo ou disparar notificações.
:::

## Fechamento

:::resumo
- Chaves estrangeiras: garantem que referências entre tabelas são válidas
- ON DELETE CASCADE: propaga exclusão para registros filhos
- ON DELETE RESTRICT: impede exclusão com dependentes ativos
- Triggers: funções automáticas que disparam em eventos (INSERT, UPDATE, DELETE)
- Triggers servem para auditoria, validação complexa e sincronização
- Prefira constraints (CHECK, FK) sempre que possível — são mais performáticas e previsíveis
- Próxima aula: projeto final — modelagem de sistema escolar do DER ao SQL
:::
