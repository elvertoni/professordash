import os
import re
from django.core.management.base import BaseCommand, CommandError
from turmas.models import Turma
from aulas.models import Aula
from core.validadores import validar_markdown_aula


class Command(BaseCommand):
    help = "Importa múltiplos arquivos .md de um diretório como aulas de uma turma."

    def add_arguments(self, parser):
        parser.add_argument("turma_id", type=int, help="ID da Turma no banco de dados.")
        parser.add_argument("pasta", type=str, help="Caminho do diretório com os arquivos .md.")

    def handle(self, *args, **options):
        turma_id = options["turma_id"]
        pasta = options["pasta"]

        try:
            turma = Turma.objects.get(pk=turma_id)
        except Turma.DoesNotExist:
            raise CommandError(f"Turma com ID {turma_id} não encontrada.")

        if not os.path.isdir(pasta):
            raise CommandError(f"O caminho '{pasta}' não é um diretório válido.")

        arquivos = [f for f in os.listdir(pasta) if f.endswith(".md")]
        if not arquivos:
            self.stdout.write(self.style.WARNING("Nenhum arquivo .md encontrado no diretório informado."))
            return

        self.stdout.write(self.style.SUCCESS(f"Iniciando importação de {len(arquivos)} arquivos para a turma '{turma.nome}'..."))

        sucessos = 0
        falhas = 0

        for arquivo_nome in sorted(arquivos):
            caminho_completo = os.path.join(pasta, arquivo_nome)
            self.stdout.write(f"\nProcessando {arquivo_nome}...")

            try:
                with open(caminho_completo, "r", encoding="utf-8", errors="replace") as f:
                    conteudo = f.read()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro ao ler arquivo: {e}"))
                falhas += 1
                continue

            # Validação do markdown
            erros = validar_markdown_aula(conteudo)
            erros_graves = [e for e in erros if any(k in e.lower() for k in ["vazio", "h1", "questão", "html bruto", "inválido", "roteiro", "início da linha"])]

            if erros_graves:
                self.stdout.write(self.style.ERROR(f"Arquivo '{arquivo_nome}' rejeitado devido a violações graves do formato:"))
                for erro in erros_graves:
                    self.stdout.write(self.style.ERROR(f"  - {erro}"))
                falhas += 1
                continue

            # Avisos (violações não-graves)
            avisos = [e for e in erros if e not in erros_graves]
            if avisos:
                self.stdout.write(self.style.WARNING(f"Avisos de formato para '{arquivo_nome}':"))
                for aviso in avisos:
                    self.stdout.write(self.style.WARNING(f"  - {aviso}"))

            # Extrair título do H1
            match = re.search(r"^#\s+(.+)$", conteudo, re.MULTILINE)
            if match:
                titulo = match.group(1).strip()
            else:
                titulo = arquivo_nome.removesuffix(".md")

            # Obter próximo número
            proximo_numero = (
                turma.aulas.order_by("-numero").values_list("numero", flat=True).first()
                or 0
            ) + 1

            try:
                aula = Aula.objects.create(
                    turma=turma,
                    titulo=titulo,
                    conteudo=conteudo,
                    numero=proximo_numero,
                    ordem=proximo_numero,
                )
                self.stdout.write(self.style.SUCCESS(f"Sucesso: Aula {aula.numero} — '{titulo}' importada com ID {aula.pk}."))
                sucessos += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro ao criar registro no banco de dados para '{arquivo_nome}': {e}"))
                falhas += 1

        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"Importação concluída: {sucessos} com sucesso, {falhas} falhas."))
