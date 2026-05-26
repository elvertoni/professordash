import secrets
from django.conf import settings
from django.db import models


class BaseModel(models.Model):
    """Modelo abstrato base. Todos os models do projeto devem herdar desta classe."""

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ApiToken(models.Model):
    """Token de autenticação para acesso via API."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="api_token",
        verbose_name="Usuário",
    )
    key = models.CharField(max_length=40, unique=True, primary_key=True, verbose_name="Chave")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name="Último uso em")

    class Meta:
        verbose_name = "Token de API"
        verbose_name_plural = "Tokens de API"

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(20)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Token de {self.user.email} ({self.key[:8]}...)"
