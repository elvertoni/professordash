import uuid

from django.db import models
from django.urls import reverse

from core.models import BaseModel


class Turma(BaseModel):
    """Representa uma turma/disciplina gerenciada pelo professor."""

    nome = models.CharField(max_length=200)
    codigo = models.CharField(max_length=20, unique=True)
    descricao = models.TextField(blank=True)
    periodo = models.CharField(max_length=20)
    ano_letivo = models.IntegerField()
    token_publico = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    ativa = models.BooleanField(default=True)
    alunos = models.ManyToManyField(
        "alunos.Aluno",
        through="Matricula",
        related_name="turmas",
        blank=True,
    )

    class Meta:
        ordering = ["-ano_letivo", "nome"]
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"

    def __str__(self) -> str:
        return f"{self.nome} ({self.ano_letivo})"

    @property
    def link_publico(self) -> str:
        """Retorna a URL pública da turma baseada no token UUID."""
        return reverse("turmas:portal", kwargs={"token": self.token_publico})


class Matricula(BaseModel):
    """Registro de matrícula de um aluno em uma turma (tabela intermediária)."""

    aluno = models.ForeignKey(
        "alunos.Aluno",
        on_delete=models.CASCADE,
        related_name="matriculas",
    )
    turma = models.ForeignKey(
        Turma,
        on_delete=models.CASCADE,
        related_name="matriculas",
    )
    data_entrada = models.DateField(auto_now_add=True)
    ativa = models.BooleanField(default=True)

    class Meta:
        unique_together = ("aluno", "turma")
        ordering = ["aluno__nome"]
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"

    def __str__(self) -> str:
        return f"{self.aluno} — {self.turma}"
