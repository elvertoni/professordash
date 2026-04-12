from django.db import migrations


def drop_orphan_columns(apps, schema_editor):
    """
    Remove colunas órfãs de turmas_turma que sobraram de versões antigas
    do model: `serie`, `disciplina`, `classroom_course_id`. Estão no banco
    de produção como NOT NULL sem default, então qualquer INSERT novo
    (criar turma programaticamente) falha com IntegrityError.

    No SQLite (dev/testes) as colunas não existem em DBs criados a partir
    do schema atual, então pulamos silenciosamente.
    """
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            ALTER TABLE turmas_turma
            DROP COLUMN IF EXISTS serie,
            DROP COLUMN IF EXISTS disciplina,
            DROP COLUMN IF EXISTS classroom_course_id;
            """
        )


class Migration(migrations.Migration):
    dependencies = [
        ("turmas", "0002_fix_gerador_fk"),
    ]

    operations = [
        migrations.RunPython(drop_orphan_columns, migrations.RunPython.noop),
    ]
