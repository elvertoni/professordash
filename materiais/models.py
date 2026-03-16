from django.db import models
from markdownx.models import MarkdownxField

from core.models import BaseModel


class TipoMaterial(models.TextChoices):
    PDF = "pdf", "PDF / Slides"
    ZIP = "zip", "Arquivo ZIP / Código"
    MARKDOWN = "markdown", "Conteúdo Markdown/HTML"
    LINK = "link", "Link Externo"
    ARQUIVO = "arquivo", "Outro Arquivo"


class VisibilidadeMaterial(models.TextChoices):
    PUBLICO = "publico", "Público (link da turma)"
    RESTRITO = "restrito", "Restrito (requer login Google)"


class Material(BaseModel):
    turma = models.ForeignKey(
        "turmas.Turma",
        on_delete=models.CASCADE,
        related_name="materiais",
    )
    aula = models.ForeignKey(
        "aulas.Aula",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="materiais",
    )
    titulo = models.CharField(max_length=300)
    descricao = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TipoMaterial.choices)
    visibilidade = models.CharField(
        max_length=20,
        choices=VisibilidadeMaterial.choices,
        default=VisibilidadeMaterial.PUBLICO,
    )
    arquivo = models.FileField(upload_to="materiais/%Y/%m/", null=True, blank=True)
    url_externa = models.URLField(blank=True)
    conteudo_md = MarkdownxField(blank=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "criado_em"]
        verbose_name = "Material"
        verbose_name_plural = "Materiais"

    def __str__(self) -> str:
        return self.titulo
