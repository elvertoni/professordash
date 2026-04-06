"""
Management command para sincronizar aulas do GitHub ProfToniCoimbra.

Uso:
    python manage.py importar_aulas_github
    python manage.py importar_aulas_github --turma AMS-1A-M-2026
    python manage.py importar_aulas_github --turma AMS-1A-M-2026 --dry-run
"""

from django.core.management.base import BaseCommand

from aulas.github_sync import build_lessons_index, fetch_manifest, sync_turma
from turmas.models import Turma


class Command(BaseCommand):
    help = "Sincroniza aulas do repositório GitHub ProfToniCoimbra para as turmas cadastradas"

    def add_arguments(self, parser):
        parser.add_argument(
            "--turma",
            type=str,
            help="Código da turma específica (ex: AMS-1A-M-2026). Omitir sincroniza todas.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Apenas lista o que seria sincronizado, sem alterar o banco",
        )

    def handle(self, *args, **options):
        codigo_filtro = options.get("turma")
        dry_run = options.get("dry_run")

        self.stdout.write("Baixando manifest.json do GitHub...")
        try:
            manifest = fetch_manifest()
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"Falha ao baixar manifest: {exc}"))
            return

        lessons_index = build_lessons_index(manifest)
        self.stdout.write(
            f"Manifest carregado: {sum(len(v) for v in lessons_index.values())} aulas em "
            f"{len(lessons_index)} subjects."
        )

        turmas_qs = Turma.objects.filter(ativa=True)
        if codigo_filtro:
            turmas_qs = turmas_qs.filter(codigo=codigo_filtro)
            if not turmas_qs.exists():
                self.stderr.write(self.style.ERROR(f"Turma '{codigo_filtro}' não encontrada."))
                return

        total_criadas = total_atualizadas = total_erros = ignoradas = 0

        for turma in turmas_qs:
            if dry_run:
                from aulas.github_sync import get_subject_from_codigo
                subject = get_subject_from_codigo(turma.codigo)
                count = len(lessons_index.get(subject, [])) if subject else 0
                label = subject or "(sem mapeamento)"
                self.stdout.write(f"  {turma.codigo} → {label}: {count} aulas disponíveis")
                continue

            resultado = sync_turma(turma, lessons_index)

            if resultado["ignorada"]:
                ignoradas += 1
                self.stdout.write(
                    self.style.WARNING(f"  {turma.codigo} → sem mapeamento GitHub, ignorada")
                )
            else:
                total_criadas += resultado["criadas"]
                total_atualizadas += resultado["atualizadas"]
                total_erros += resultado["erros"]
                self.stdout.write(
                    f"  {turma.codigo} → {resultado['subject']}: "
                    f"+{resultado['criadas']} criadas, "
                    f"~{resultado['atualizadas']} atualizadas, "
                    f"{resultado['erros']} erros"
                )

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nConcluído: {total_criadas} criadas, {total_atualizadas} atualizadas, "
                    f"{total_erros} erros, {ignoradas} turmas sem mapeamento."
                )
            )
