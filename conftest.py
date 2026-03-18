"""
Fixtures globais para todos os testes do ProfessorDash.

Disponíveis automaticamente em todos os módulos de teste via pytest conftest.py.
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@pytest.fixture
def professor(db):
    """Usuário com is_staff=True — representa o professor no sistema."""
    return User.objects.create_user(
        username="prof_toni",
        email="toni@seed.pr.gov.br",
        password="senha123!",
        is_staff=True,
        is_active=True,
    )


@pytest.fixture
def aluno_user(db):
    """Usuário comum — representa o aluno autenticado via Google OAuth."""
    return User.objects.create_user(
        username="joao.aluno",
        email="joao@escola.pr.gov.br",
        password="senha123!",
        is_active=True,
        first_name="João",
        last_name="Silva",
    )


@pytest.fixture
def aluno(db, aluno_user):
    """Aluno vinculado ao aluno_user."""
    from alunos.models import Aluno

    return Aluno.objects.create(
        user=aluno_user,
        nome="João Silva",
        email="joao@escola.pr.gov.br",
        matricula="2024001",
    )


@pytest.fixture
def aluno_sem_matricula_user(db):
    """Usuário aluno com vínculo em Aluno, mas sem matrícula ativa."""
    return User.objects.create_user(
        username="maria.sem.matricula",
        email="maria.sem.matricula@escola.pr.gov.br",
        password="senha123!",
        is_active=True,
        first_name="Maria",
        last_name="Sem Matricula",
    )


@pytest.fixture
def aluno_sem_matricula(db, aluno_sem_matricula_user):
    """Aluno sem matrícula em turma alguma."""
    from alunos.models import Aluno

    return Aluno.objects.create(
        user=aluno_sem_matricula_user,
        nome="Maria Sem Matricula",
        email="maria.sem.matricula@escola.pr.gov.br",
        matricula="2024999",
    )


@pytest.fixture
def turma(db):
    """Turma ativa criada pelo professor."""
    from turmas.models import Turma

    return Turma.objects.create(
        nome="Programação Web",
        codigo="PW2024A",
        descricao="Turma de programação web do 3º ano",
        periodo="1",
        ano_letivo=2024,
        ativa=True,
    )


@pytest.fixture
def matricula(db, aluno, turma):
    """Matrícula ativa do aluno na turma."""
    from turmas.models import Matricula

    return Matricula.objects.create(
        aluno=aluno,
        turma=turma,
        ativa=True,
    )


@pytest.fixture
def atividade_aberta(db, turma):
    """Atividade publicada com prazo futuro (7 dias a partir de agora)."""
    from atividades.models import Atividade, TipoEntrega

    return Atividade.objects.create(
        turma=turma,
        titulo="Projeto Final",
        descricao="Entregue o projeto final da disciplina.",
        tipo_entrega=TipoEntrega.TEXTO,
        prazo=timezone.now() + timedelta(days=7),
        valor_pontos=10.0,
        permitir_reenvio=True,
        publicada=True,
    )


@pytest.fixture
def client_professor(client, professor):
    """Django test client autenticado como professor (is_staff=True)."""
    client.force_login(professor)
    return client


@pytest.fixture
def client_aluno(client, aluno_user):
    """Django test client autenticado como aluno_user."""
    client.force_login(aluno_user)
    return client


@pytest.fixture
def client_aluno_sem_matricula(client, aluno_sem_matricula_user):
    """Django test client autenticado como aluno sem matrícula ativa."""
    client.force_login(aluno_sem_matricula_user)
    return client
