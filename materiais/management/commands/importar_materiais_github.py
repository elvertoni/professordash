"""
Management command para sincronizar materiais HTML do GitHub ProfToniCoimbra.

Uso:
    python manage.py importar_materiais_github
    python manage.py importar_materiais_github --turma AMS-1A-M-2026
    python manage.py importar_materiais_github --turma AMS-1A-M-2026 --dry-run
"""

from django.core.management.base import BaseCommand

from aulas.github_sync import get_subject_from_codigo
from materiais.github_sync import build_materials_index, fetch_tree, sync_turma
from turmas.models import Turma


class Command(BaseCommand):
    help = "Sincroniza materiais HTML estaticos do repositorio GitHub ProfToniCoimbra"

    def add_arguments(self, parser):
        parser.add_argument(
            "--turma",
            type=str,
            help="Codigo da turma especifica (ex: AMS-1A-M-2026). Omitir sincroniza todas.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Apenas lista o que seria sincronizado, sem alterar o banco",
        )

    def handle(self, *args, **options):
        codigo_filtro = options.get("turma")
        dry_run = options.get("dry_run")

        self.stdout.write("Baixando arvore de arquivos do GitHub...")
        try:
            tree = fetch_tree()
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"Falha ao baixar tree: {exc}"))
            return

        materials_index = build_materials_index(tree)
        total_materiais = sum(len(v) for v in materials_index.values())
        self.stdout.write(
            f"Arvore carregada: {total_materiais} materiais HTML em "
            f"{len(materials_index)} subjects."
        )

        turmas_qs = Turma.objects.filter(ativa=True)
        if codigo_filtro:
            turmas_qs = turmas_qs.filter(codigo=codigo_filtro)
            if not turmas_qs.exists():
                self.stderr.write(self.style.ERROR(f"Turma '{codigo_filtro}' nao encontrada."))
                return

        total_criadas = total_atualizadas = total_erros = ignoradas = 0

        for turma in turmas_qs:
            if dry_run:
                subject = get_subject_from_codigo(turma.codigo)
                count = len(materials_index.get(subject.lower(), [])) if subject else 0
                label = subject or "(sem mapeamento)"
                self.stdout.write(f"  {turma.codigo} -> {label}: {count} materiais disponiveis")
                continue

            resultado = sync_turma(turma, materials_index)

            if resultado["ignorada"]:
                ignoradas += 1
                self.stdout.write(
                    self.style.WARNING(f"  {turma.codigo} -> sem mapeamento GitHub, ignorada")
                )
            else:
                total_criadas += resultado["criadas"]
                total_atualizadas += resultado["atualizadas"]
                total_erros += resultado["erros"]
                self.stdout.write(
                    f"  {turma.codigo} -> {resultado['subject']}: "
                    f"+{resultado['criadas']} criadas, "
                    f"~{resultado['atualizadas']} atualizadas, "
                    f"{resultado['erros']} erros"
                )

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nDry-run concluido: {turmas_qs.count()} turmas analisadas, "
                    f"{sum(len(v) for v in materials_index.values())} materiais HTML encontrados."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"\nConcluido: {total_criadas} criadas, {total_atualizadas} atualizadas, "
                f"{total_erros} erros, {ignoradas} turmas sem mapeamento."
            )
        )
