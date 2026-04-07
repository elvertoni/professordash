from django.db import migrations


def drop_gerador_fk(apps, schema_editor):
    """
    Remove o FK constraint da tabela gerador_sessaogeracao que referencia
    turmas_turma. Essa tabela pertencia ao app gerador_aulas (removido),
    mas o constraint ficou no banco de producao (PostgreSQL) bloqueando
    a exclusao de turmas.

    No SQLite (dev/testes) a tabela nao existe e o ALTER TABLE nao suporta
    DROP CONSTRAINT, portanto pulamos silenciosamente.
    """
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.table_constraints
                    WHERE table_name = 'gerador_sessaogeracao'
                      AND constraint_name = 'gerador_sessaogeracao_disciplina_id_eb8d6085_fk_turmas_turma_id'
                ) THEN
                    ALTER TABLE gerador_sessaogeracao
                    DROP CONSTRAINT gerador_sessaogeracao_disciplina_id_eb8d6085_fk_turmas_turma_id;
                END IF;
            END;
            $$;
            """
        )


class Migration(migrations.Migration):
    """
    Remove o FK constraint da tabela gerador_sessaogeracao que referencia
    turmas_turma. Essa tabela pertencia ao app gerador_aulas (removido),
    mas o constraint ficou no banco bloqueando a exclusão de turmas.
    Executa apenas em PostgreSQL; é ignorada em SQLite (dev/testes).
    """

    dependencies = [
        ("turmas", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(drop_gerador_fk, migrations.RunPython.noop),
    ]
