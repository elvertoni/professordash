from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("atividades", "0003_alter_atividade_aula_alter_entrega_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="atividade",
            name="conteudo_html",
            field=models.TextField(
                blank=True,
                help_text="HTML estático renderizado em lugar da descrição Markdown. Preenchido pela sync do GitHub.",
            ),
        ),
        migrations.AddField(
            model_name="atividade",
            name="origem_github",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="Path do arquivo no repositório GitHub (chave idempotente da sync).",
                max_length=500,
            ),
        ),
        migrations.AddConstraint(
            model_name="atividade",
            constraint=models.UniqueConstraint(
                condition=models.Q(("origem_github__gt", "")),
                fields=("turma", "origem_github"),
                name="atividade_unique_por_origem_github",
            ),
        ),
    ]
