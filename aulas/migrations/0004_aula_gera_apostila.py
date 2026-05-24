# Generated manually during ProfessorDash v2.0 refactor on 2026-05-24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("aulas", "0003_drop_classroom_orphan"),
    ]

    operations = [
        migrations.AddField(
            model_name="aula",
            name="gera_apostila",
            field=models.BooleanField(
                default=True,
                help_text="Permite exportar esta aula como HTML standalone.",
                verbose_name="Gerar apostila",
            ),
        ),
    ]
