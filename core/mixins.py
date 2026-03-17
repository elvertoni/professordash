from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


class ProfessorRequiredMixin(LoginRequiredMixin):
    """Restringe acesso às views /painel/ ao professor (is_staff=True)."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class TurmaPublicaMixin:
    """Resolve self.turma a partir do token_publico na URL. Usado em views públicas."""

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # Import local para evitar dependência circular
        from turmas.models import Turma
        self.turma = get_object_or_404(
            Turma, token_publico=kwargs["token"], ativa=True
        )


class AlunoAutenticadoMixin(TurmaPublicaMixin, LoginRequiredMixin):
    """Garante que o usuário autenticado possui matrícula ativa na turma."""

    def dispatch(self, request, *args, **kwargs):
        # setup() é chamado antes do dispatch, então self.turma já está disponível
        response = super().dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return response
        from turmas.models import Matricula
        try:
            self.matricula = Matricula.objects.select_related("aluno").get(
                aluno__user=request.user,
                turma=self.turma,
                ativa=True,
            )
        except Matricula.DoesNotExist:
            raise PermissionDenied
        return response
