from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Após login Google, vincula o User ao Aluno cadastrado com o mesmo email.
    Isso permite que AlunoAutenticadoMixin encontre a matrícula via aluno__user.
    """

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        self._vincular_aluno(user)
        return user

    def pre_social_login(self, request, sociallogin):
        """Valida domínio do email institucional antes de prosseguir."""
        # Extrair email do sociallogin
        email = (sociallogin.account.extra_data.get("email", "") or "").lower()
        if not email and sociallogin.user and sociallogin.user.email:
            email = sociallogin.user.email.lower()

        if not email:
            # Sem email — bloqueia (caso raro no Google OAuth)
            messages.error(
                request,
                "Não foi possível identificar seu e-mail. "
                "Use sua conta @escola.pr.gov.br para acessar.",
            )
            raise ImmediateHttpResponse(self._redirect_to_turma(request))

        allowed = getattr(
            settings, "GOOGLE_ALLOWED_DOMAINS", ["escola.pr.gov.br"]
        )
        if not any(email.endswith(f"@{domain}") for domain in allowed):
            domain_part = email.split("@")[-1] if "@" in email else email
            messages.error(
                request,
                f"Seu e-mail ({domain_part}) não é um e-mail institucional "
                f"permitido. Use sua conta @{allowed[0]} para acessar.",
            )
            raise ImmediateHttpResponse(self._redirect_to_turma(request))

        # Domínio válido — prossegue com o fluxo normal
        super().pre_social_login(request, sociallogin)
        if sociallogin.is_existing:
            self._vincular_aluno(sociallogin.user)

    @staticmethod
    def _vincular_aluno(user):
        if not user or not user.pk or not user.email:
            return
        try:
            from alunos.models import Aluno

            aluno = Aluno.objects.get(email__iexact=user.email, user__isnull=True)
            aluno.user = user
            aluno.save(update_fields=["user"])
        except (Aluno.DoesNotExist, Aluno.MultipleObjectsReturned):
            pass

    @staticmethod
    def _redirect_to_turma(request):
        """Redireciona para a página de entrada da turma, com fallback seguro."""
        token = request.session.get("turma_token", "")
        if token:
            return redirect(reverse("turmas:entrar", kwargs={"token": token}))
        return redirect("/")
