"""
Fixtures globais do pytest-django para o projeto ProfessorDash.

Disponíveis em todos os testes sem necessidade de importação.
"""
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from alunos.models import Aluno
from atividades.models import Atividade
from turmas.models import Matricula, Turma

User = get_user_model()


# ---------------------------------------------------------------------------
# Usuários
# ---------------------------------------------------------------------------


@pytest.fixture
def professor(db):
    """Usuário professor (is_staff=True)."""
    return User.objects.create_user(
        username="professor",
        email="professor@escola.pr.gov.br",
        password="senha123",
        is_staff=True,
    )


@pytest.fixture
def aluno_user(db):
    """Usuário comum que representa um aluno."""
    return User.objects.create_user(
        username="aluno",
        email="aluno@escola.pr.gov.br",
        password="senha123",
        is_staff=False,
    )


@pytest.fixture
def aluno_user_sem_matricula(db):
    """Usuário autenticado mas sem matrícula na turma."""
    return User.objects.create_user(
        username="semmatricula",
        email="semmatricula@escola.pr.gov.br",
        password="senha123",
        is_staff=False,
    )


# ---------------------------------------------------------------------------
# Entidades do domínio
# ---------------------------------------------------------------------------


@pytest.fixture
def aluno(db, aluno_user):
    """Aluno vinculado ao aluno_user."""
    return Aluno.objects.create(
        user=aluno_user,
        nome="Aluno Teste",
        email=aluno_user.email,
    )


@pytest.fixture
def turma(db):
    """Turma ativa com token_publico gerado automaticamente."""
    return Turma.objects.create(
        nome="Informatica Aplicada",
        codigo="INF-2024-A",
        periodo="1",
        ano_letivo=2024,
        ativa=True,
    )


@pytest.fixture
def matricula(db, aluno, turma):
    """Matrícula ativa do aluno na turma."""
    return Matricula.objects.create(
        aluno=aluno,
        turma=turma,
        ativa=True,
    )


@pytest.fixture
def atividade_aberta(db, turma):
    """Atividade publicada com prazo futuro (tipo texto para facilitar entrega nos testes)."""
    return Atividade.objects.create(
        turma=turma,
        titulo="Atividade de Teste",
        descricao="Descreva o assunto estudado.",
        tipo_entrega="texto",
        prazo=timezone.now() + timezone.timedelta(days=7),
        valor_pontos=10,
        publicada=True,
        permitir_reenvio=True,
    )


# ---------------------------------------------------------------------------
# Clients autenticados
# ---------------------------------------------------------------------------


@pytest.fixture
def client_professor(client, professor):
    """Client HTTP autenticado como professor (is_staff=True)."""
    client.force_login(professor)
    return client


@pytest.fixture
def client_aluno(client, aluno_user, matricula):
    """Client HTTP autenticado como aluno COM matrícula na turma."""
    client.force_login(aluno_user)
    return client


@pytest.fixture
def client_aluno_sem_matricula(client, aluno_user_sem_matricula):
    """Client HTTP autenticado como usuário SEM matrícula em nenhuma turma."""
    client.force_login(aluno_user_sem_matricula)
    return client
