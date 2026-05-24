from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string

from aulas.models import Aula
from aulas.views import _build_apostila_context


class Command(BaseCommand):
    help = "Exporta uma aula como apostila HTML standalone."

    def add_arguments(self, parser):
        parser.add_argument("aula_id", type=int)
        parser.add_argument("output_path")

    def handle(self, *args, **options):
        aula_id = options["aula_id"]
        output_path = Path(options["output_path"])

        try:
            aula = Aula.objects.select_related("turma").get(
                pk=aula_id,
                gera_apostila=True,
            )
        except Aula.DoesNotExist as exc:
            raise CommandError(
                f"Aula {aula_id} não encontrada ou com apostila desabilitada."
            ) from exc

        output_path.parent.mkdir(parents=True, exist_ok=True)
        html = render_to_string("aulas/apostila.html", _build_apostila_context(aula))
        output_path.write_text(html, encoding="utf-8")

        self.stdout.write(self.style.SUCCESS(f"Apostila exportada: {output_path}"))
