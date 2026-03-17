from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import Aluno


@receiver(user_logged_in)
def vincular_ou_criar_aluno_apos_login(sender, user, request, **kwargs):
    """
    Sinal executado logo após o login do usuário (inclusive via Google OAuth).
    Objetivo:
    - Busca o aluno pelo e-mail do usuário.
    - Se encontrar o Aluno e não tiver usuário vinculado, vincula.
    - Se não encontrar o Aluno pelo e-mail, cria um novo Aluno automaticamente
      já vinculado a este usuário.
    """
    if not user.email or user.is_staff:
        return

    aluno = Aluno.objects.filter(email=user.email).first()

    if aluno:
        # Se o aluno já existe (ex: importado via CSV), vincula
        if not aluno.user:
            aluno.user = user
            aluno.save(update_fields=["user"])
    else:
        # Se o aluno não existe ainda, cria automaticamente
        nome = user.get_full_name() or user.username or user.email.split("@")[0]
        Aluno.objects.get_or_create(
            user=user,
            defaults={"email": user.email, "nome": nome},
        )
