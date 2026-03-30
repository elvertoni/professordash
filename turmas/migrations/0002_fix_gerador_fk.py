from django.db import migrations


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
        migrations.RunSQL(
            sql="""
                ALTER TABLE gerador_sessaogeracao
                DROP CONSTRAINT IF EXISTS gerador_sessaogeracao_disciplina_id_eb8d6085_fk_turmas_turma_id;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
