import pytest
from django.contrib.auth import get_user_model

from alunos.models import Aluno
from alunos.signals import vincular_ou_criar_aluno_apos_login

User = get_user_model()


@pytest.mark.django_db
def test_login_vincula_aluno_case_insensitive_sem_reativar_matricula(turma):
    user = User.objects.create_user(
        username="aluno-case",
        email="Aluno@Escola.PR.GOV.BR",
        password="senha123",
    )
    aluno = Aluno.objects.create(
        nome="Aluno Existente",
        email="aluno@escola.pr.gov.br",
    )
    matricula = turma.matriculas.create(aluno=aluno, ativa=False)

    vincular_ou_criar_aluno_apos_login(sender=User, user=user, request=None)

    aluno.refresh_from_db()
    matricula.refresh_from_db()
    assert aluno.user == user
    assert aluno.email == "aluno@escola.pr.gov.br"
    assert matricula.ativa is False
    assert Aluno.objects.filter(email__iexact=user.email).count() == 1
