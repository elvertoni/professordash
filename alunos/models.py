from django.contrib.auth import get_user_model
from django.db import models

from core.models import BaseModel

User = get_user_model()


class Aluno(BaseModel):
    """Representa um aluno que pode estar matriculado em uma ou mais turmas."""

    user = models.OneToOneField(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="aluno",
    )
    nome = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    matricula = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to="avatares/", blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"

    def __str__(self) -> str:
        return self.nome
