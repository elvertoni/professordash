from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from turmas.models import Matricula

from .models import Aluno


@receiver(user_logged_in)
def vincular_ou_criar_aluno_apos_login(sender, user, request, **kwargs):
    """
    Sinal executado logo apos o login do usuario, inclusive via Google OAuth.
    """
    if not user.email or user.is_staff:
        return

    aluno = Aluno.objects.filter(email=user.email).first()

    if aluno:
        if not aluno.user:
            aluno.user = user
            aluno.save(update_fields=["user"])
        Matricula.objects.filter(aluno=aluno).update(ativa=True)
        return

    nome = user.get_full_name() or user.username or user.email.split("@")[0]
    Aluno.objects.get_or_create(
        user=user,
        defaults={"email": user.email, "nome": nome},
    )
