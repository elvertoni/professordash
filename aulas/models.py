from django.db import models
from markdownx.models import MarkdownxField

from core.models import BaseModel


class Aula(BaseModel):
    """Representa uma aula dentro de uma turma, com conteúdo em Markdown."""

    turma = models.ForeignKey(
        "turmas.Turma",
        on_delete=models.CASCADE,
        related_name="aulas",
    )
    titulo = models.CharField(max_length=300)
    numero = models.PositiveIntegerField()
    data = models.DateField(null=True, blank=True)
    conteudo = MarkdownxField(blank=True)
    realizada = models.BooleanField(default=False)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "numero"]
        unique_together = ("turma", "numero")
        verbose_name = "Aula"
        verbose_name_plural = "Aulas"

    def __str__(self) -> str:
        return f"Aula {self.numero} — {self.titulo}"
