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
    imagem_capa = models.ImageField(
        upload_to="aulas/capas/%Y/%m/",
        blank=True,
        verbose_name="Imagem de capa",
    )
    gera_apostila = models.BooleanField(
        default=True,
        verbose_name="Gerar apostila",
        help_text="Permite exportar esta aula como HTML standalone.",
    )
    realizada = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=[
            ("rascunho", "Rascunho"),
            ("publicada", "Publicada"),
            ("arquivada", "Arquivada"),
        ],
        default="rascunho",
    )
    ordem = models.PositiveIntegerField(default=0)

    @property
    def esta_realizada(self):
        return self.status == "publicada"

    class Meta:
        ordering = ["ordem", "numero"]
        unique_together = ("turma", "numero")
        verbose_name = "Aula"
        verbose_name_plural = "Aulas"

    def clean(self) -> None:
        super().clean()
        from django.core.exceptions import ValidationError
        from core.validadores import validar_markdown_aula
        
        if self.conteudo:
            erros = validar_markdown_aula(self.conteudo)
            erros_graves = []
            for erro in erros:
                # Severe errors that block saving
                if any(k in erro.lower() for k in ["vazio", "h1", "questão", "html bruto", "inválido", "roteiro", "início da linha"]):
                    erros_graves.append(erro)
            
            if erros_graves:
                raise ValidationError({
                    "conteudo": erros_graves
                })

    def __str__(self) -> str:
        return f"Aula {self.numero} — {self.titulo}"
