from django.db import migrations


def drop_classroom_orphan(apps, schema_editor):
    """
    Remove a coluna órfã `classroom_announcement_id` de aulas_aula.

    Essa coluna pertencia a uma versão antiga do modelo Aula (integração
    com Google Classroom) que foi removida do código mas nunca dropada
    do banco de produção via migration. Como ficou NOT NULL sem default,
    qualquer INSERT novo (ex.: sincronização do GitHub) falha com
    IntegrityError.

    No SQLite (dev/testes) a coluna não existe em DBs criados a partir
    do schema atual, então pulamos silenciosamente.
    """
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            ALTER TABLE aulas_aula
            DROP COLUMN IF EXISTS classroom_announcement_id;
            """
        )


class Migration(migrations.Migration):
    dependencies = [
        ("aulas", "0002_aula_imagem_capa"),
    ]

    operations = [
        migrations.RunPython(drop_classroom_orphan, migrations.RunPython.noop),
    ]
