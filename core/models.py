from django.db import models


class BaseModel(models.Model):
    """Modelo abstrato base. Todos os models do projeto devem herdar desta classe."""

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
