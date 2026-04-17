from django.db import models
from django.utils import timezone
from markdownx.models import MarkdownxField

from core.models import BaseModel


class TipoEntrega(models.TextChoices):
    ARQUIVO = "arquivo", "Envio de Arquivo"
    TEXTO = "texto", "Texto / Resposta"
    LINK = "link", "Link (GitHub, Replit...)"


class StatusEntrega(models.TextChoices):
    PENDENTE = "pendente", "Pendente"
    ENTREGUE = "entregue", "Entregue"
    ATRASADA = "atrasada", "Entregue em Atraso"
    AVALIADA = "avaliada", "Avaliada"


class Atividade(BaseModel):
    """Representa uma atividade avaliativa ou tarefa para uma turma."""

    turma = models.ForeignKey(
        "turmas.Turma",
        on_delete=models.CASCADE,
        related_name="atividades",
    )
    aula = models.ForeignKey(
        "aulas.Aula",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="atividades",
    )
    titulo = models.CharField(max_length=300)
    descricao = MarkdownxField()
    tipo_entrega = models.CharField(
        max_length=20,
        choices=TipoEntrega.choices,
        default=TipoEntrega.ARQUIVO,
    )
    prazo = models.DateTimeField()
    valor_pontos = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.0,
    )
    permitir_reenvio = models.BooleanField(default=True)
    publicada = models.BooleanField(default=True)
    conteudo_html = models.TextField(
        blank=True,
        help_text="HTML estático renderizado em lugar da descrição Markdown. Preenchido pela sync do GitHub.",
    )
    origem_github = models.CharField(
        max_length=500,
        blank=True,
        db_index=True,
        help_text="Path do arquivo no repositório GitHub (chave idempotente da sync).",
    )

    class Meta:
        ordering = ["-prazo", "-criado_em"]
        verbose_name = "Atividade"
        verbose_name_plural = "Atividades"
        constraints = [
            models.UniqueConstraint(
                fields=["turma", "origem_github"],
                condition=models.Q(origem_github__gt=""),
                name="atividade_unique_por_origem_github",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.titulo} - {self.turma}"

    @property
    def esta_aberta(self) -> bool:
        """Verifica se a atividade está publicada e o prazo não expirou."""
        return bool(self.publicada and timezone.now() <= self.prazo)


class Entrega(BaseModel):
    """Representa a entrega/envio de uma atividade por um aluno."""

    atividade = models.ForeignKey(
        Atividade,
        on_delete=models.CASCADE,
        related_name="entregas",
    )
    aluno = models.ForeignKey(
        "alunos.Aluno",
        on_delete=models.CASCADE,
        related_name="entregas",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusEntrega.choices,
        default=StatusEntrega.PENDENTE,
    )
    arquivo = models.FileField(
        upload_to="entregas/%Y/%m/",
        null=True,
        blank=True,
    )
    texto = models.TextField(blank=True)
    url = models.URLField(blank=True)
    data_envio = models.DateTimeField(default=timezone.now)
    prazo_extendido = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Prazo individual para este aluno. Se preenchido, substitui o prazo geral da atividade.",
    )

    # Avaliação
    nota = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    feedback = models.TextField(blank=True)
    data_avaliacao = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("atividade", "aluno")
        ordering = ["-data_envio"]
        verbose_name = "Entrega"
        verbose_name_plural = "Entregas"

    def __str__(self) -> str:
        return f"Entrega de {self.aluno} - {self.atividade}"
