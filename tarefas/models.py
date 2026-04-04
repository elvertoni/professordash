from django.db import models

from alunos.models import Aluno
from core.models import BaseModel
from turmas.models import Turma


class Tarefa(BaseModel):
    turma = models.ForeignKey(
        Turma,
        on_delete=models.CASCADE,
        related_name="tarefas",
    )
    nome = models.CharField(max_length=200)
    data = models.DateField(null=True, blank=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "criado_em"]
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"

    def __str__(self) -> str:
        return self.nome


class RealizacaoTarefa(BaseModel):
    tarefa = models.ForeignKey(
        Tarefa,
        on_delete=models.CASCADE,
        related_name="realizacoes",
    )
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        related_name="realizacoes_tarefas",
    )
    realizada = models.BooleanField(default=False)

    class Meta:
        unique_together = ("tarefa", "aluno")
        verbose_name = "Realização de Tarefa"
        verbose_name_plural = "Realizações de Tarefas"

    def __str__(self) -> str:
        return f"{self.aluno} - {self.tarefa}"
