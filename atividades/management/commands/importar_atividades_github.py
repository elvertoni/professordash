"""
Management command para sincronizar atividades HTML do GitHub ProfToniCoimbra.

Uso:
    python manage.py importar_atividades_github
    python manage.py importar_atividades_github --turma AMS-1A-M-2026
    python manage.py importar_atividades_github --turma AMS-1A-M-2026 --dry-run
"""

from django.core.management.base import BaseCommand

from atividades.github_sync import build_activities_index, fetch_tree, sync_turma
from aulas.github_sync import get_subject_from_codigo
from turmas.models import Turma


class Command(BaseCommand):
    help = "Sincroniza atividades HTML estáticas do repositório GitHub ProfToniCoimbra"

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

        self.stdout.write("Baixando árvore de arquivos do GitHub...")
        try:
            tree = fetch_tree()
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"Falha ao baixar tree: {exc}"))
            return

        activities_index = build_activities_index(tree)
        total_atividades = sum(len(v) for v in activities_index.values())
        self.stdout.write(
            f"Árvore carregada: {total_atividades} atividades HTML em "
            f"{len(activities_index)} subjects."
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
                subject = get_subject_from_codigo(turma.codigo)
                count = len(activities_index.get(subject, [])) if subject else 0
                label = subject or "(sem mapeamento)"
                self.stdout.write(f"  {turma.codigo} → {label}: {count} atividades disponíveis")
                continue

            resultado = sync_turma(turma, activities_index)

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
