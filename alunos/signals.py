from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import Aluno


@receiver(user_logged_in)
def vincular_ou_criar_aluno_apos_login(sender, user, request, **kwargs):
    """
    Sinal executado logo apos o login do usuario, inclusive via Google OAuth.
    """
    if not user.email or user.is_staff:
        return

    email_normalizado = user.email.strip().lower()
    aluno = Aluno.objects.filter(email__iexact=email_normalizado).first()

    if aluno:
        if not aluno.user:
            aluno.user = user
            update_fields = ["user"]
            if aluno.email != email_normalizado:
                aluno.email = email_normalizado
                update_fields.append("email")
            aluno.save(update_fields=update_fields)
        return

    nome = user.get_full_name() or user.username or user.email.split("@")[0]
    Aluno.objects.get_or_create(
        user=user,
        defaults={"email": email_normalizado, "nome": nome},
    )
