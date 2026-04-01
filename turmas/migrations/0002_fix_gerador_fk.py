from django.db import migrations


def remover_fk_gerador(apps, schema_editor):
    connection = schema_editor.connection

    if connection.vendor != "postgresql":
        return

    tabelas = connection.introspection.table_names()
    if "gerador_sessaogeracao" not in tabelas:
        return

    schema_editor.execute(
        """
        ALTER TABLE gerador_sessaogeracao
        DROP CONSTRAINT IF EXISTS gerador_sessaogeracao_disciplina_id_eb8d6085_fk_turmas_turma_id;
        """
    )


class Migration(migrations.Migration):
    """
    Remove o FK constraint da tabela gerador_sessaogeracao que referencia
    turmas_turma. Essa tabela pertencia ao app gerador_aulas (removido),
    mas o constraint ficou no banco bloqueando a exclusão de turmas.
    """

    dependencies = [
        ("turmas", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(remover_fk_gerador, migrations.RunPython.noop),
    ]
