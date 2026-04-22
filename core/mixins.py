from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse


class ProfessorRequiredMixin(LoginRequiredMixin):
    """Restringe acesso as views /painel/ ao professor (is_staff=True)."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class TurmaPublicaMixin:
    """Resolve self.turma a partir do token_publico na URL. Usado em views publicas."""

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        from turmas.models import Turma

        self.turma = get_object_or_404(Turma, token_publico=kwargs["token"], ativa=True)


class AlunoAutenticadoMixin(TurmaPublicaMixin, LoginRequiredMixin):
    """Garante que o usuario autenticado possui matricula ativa na turma."""

    def get_login_url(self):
        return reverse("turmas:entrar", kwargs={"token": self.turma.token_publico})

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        from turmas.models import Matricula

        try:
            self.matricula = Matricula.objects.select_related("aluno").get(
                aluno__user=request.user,
                aluno__ativo=True,
                turma=self.turma,
                ativa=True,
            )
        except Matricula.DoesNotExist:
            messages.error(
                request,
                "Seu acesso a esta turma nao esta liberado. "
                "Confira seu cadastro e sua matricula com o professor.",
            )
            return redirect("turmas:portal", token=self.turma.token_publico)
        return super().dispatch(request, *args, **kwargs)
