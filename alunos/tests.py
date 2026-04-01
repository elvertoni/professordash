import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from alunos.forms import AlunoForm
from alunos.models import Aluno
from alunos.signals import vincular_ou_criar_aluno_apos_login
from turmas.models import Matricula, Turma

CSV_BYTES = (
    "nome,email,matricula\n"
    "Ana Silva,ana.silva@escola.pr.gov.br,1001\n"
    "Bruno Lima,bruno.lima@escola.pr.gov.br,1002\n"
).encode("utf-8")

CSV_MULTITURMA_BYTES = (
    "nome,email,matricula,turma\n"
    "Ana Silva,ana.silva@escola.pr.gov.br,1001,ProgramaÃ§Ã£o Web\n"
    "Bruno Lima,bruno.lima@escola.pr.gov.br,1002,Outra Turma\n"
).encode("utf-8")


@pytest.fixture
def outra_turma(db):
    return Turma.objects.create(
        nome="Outra Turma",
        codigo="OT2024",
        descricao="Turma paralela",
        periodo="2",
        ano_letivo=2024,
        ativa=True,
    )


@pytest.mark.django_db
class TestAlunoModel:
    def test_str_retorna_nome(self, aluno):
        assert str(aluno) == "João Silva"


@pytest.mark.django_db
class TestAlunoForm:
    def test_form_valida_dados_basicos(self):
        form = AlunoForm(
            data={
                "nome": "Teste Aluno",
                "email": "teste.aluno@escola.pr.gov.br",
                "matricula": "4001",
                "ativo": "on",
            }
        )

        assert form.is_valid(), form.errors


@pytest.mark.django_db
class TestAlunoViews:
    def test_lista_alunos_redireciona_anonimo(self, client, turma):
        url = reverse("turmas:alunos_lista", kwargs={"pk": turma.pk})

        response = client.get(url)

        assert response.status_code == 302

    def test_lista_alunos_do_professor_exibe_matriculas(
        self, client_professor, turma, matricula
    ):
        url = reverse("turmas:alunos_lista", kwargs={"pk": turma.pk})

        response = client_professor.get(url)

        assert response.status_code == 200
        assert list(response.context["matriculas"]) == [matricula]

    def test_lista_alunos_nao_renderiza_div_dentro_de_table(
        self, client_professor, turma, matricula
    ):
        url = reverse("turmas:alunos_lista", kwargs={"pk": turma.pk})

        response = client_professor.get(url)
        html = response.content.decode()

        assert response.status_code == 200
        assert 'id="tabela-alunos-container"' in html
        assert "<table" in html
        assert "<table" not in html.split('id="tabela-alunos-container"', 1)[0]

    def test_criar_aluno_matricula_novo_aluno_e_vinculo(self, client_professor, turma):
        url = reverse("turmas:alunos_novo", kwargs={"pk": turma.pk})
        data = {
            "nome": "Laura Mendes",
            "email": "laura.mendes@escola.pr.gov.br",
            "matricula": "3001",
            "ativo": "on",
        }

        response = client_professor.post(url, data)

        assert response.status_code == 302
        aluno = Aluno.objects.get(email="laura.mendes@escola.pr.gov.br")
        assert Matricula.objects.filter(aluno=aluno, turma=turma, ativa=True).exists()

    def test_criar_aluno_deveria_reativar_matricula_inativa(
        self, client_professor, turma, aluno
    ):
        Matricula.objects.create(aluno=aluno, turma=turma, ativa=False)

        url = reverse("turmas:alunos_novo", kwargs={"pk": turma.pk})
        data = {
            "nome": aluno.nome,
            "email": aluno.email,
            "matricula": aluno.matricula,
            "ativo": "on",
        }

        response = client_professor.post(url, data)

        assert response.status_code == 302
        matricula = Matricula.objects.get(aluno=aluno, turma=turma)
        assert matricula.ativa is True

    def test_importar_csv_cria_alunos_e_matriculas(self, client_professor, turma):
        arquivo = SimpleUploadedFile(
            "alunos.csv",
            CSV_BYTES,
            content_type="text/csv",
        )
        url = reverse("turmas:alunos_importar", kwargs={"pk": turma.pk})

        response = client_professor.post(url, {"arquivo_csv": arquivo})

        assert response.status_code == 302
        assert Aluno.objects.filter(email="ana.silva@escola.pr.gov.br").exists()
        assert Matricula.objects.filter(
            aluno__email="ana.silva@escola.pr.gov.br",
            turma=turma,
            ativa=True,
        ).exists()

    def test_importar_csv_deveria_reativar_matricula_inativa(
        self, client_professor, turma, aluno
    ):
        Matricula.objects.create(aluno=aluno, turma=turma, ativa=False)
        csv_reimport = (
            f"nome,email,matricula\n{aluno.nome},{aluno.email},{aluno.matricula}\n"
        ).encode("utf-8")
        arquivo = SimpleUploadedFile(
            "alunos.csv",
            csv_reimport,
            content_type="text/csv",
        )
        url = reverse("turmas:alunos_importar", kwargs={"pk": turma.pk})

        response = client_professor.post(url, {"arquivo_csv": arquivo})

        assert response.status_code == 302
        assert Matricula.objects.get(aluno=aluno, turma=turma).ativa is True

    def test_importar_multiturma_csv_cria_alunos_e_matriculas(
        self, client_professor, turma, outra_turma
    ):
        csv_multiturma_bytes = (
            f"nome,email,matricula,turma\n"
            f"Ana Silva,ana.silva@escola.pr.gov.br,1001,{turma.nome}\n"
            f"Bruno Lima,bruno.lima@escola.pr.gov.br,1002,{outra_turma.nome}\n"
        ).encode("utf-8")
        arquivo = SimpleUploadedFile(
            "alunos-multiturma.csv",
            csv_multiturma_bytes,
            content_type="text/csv",
        )
        url = reverse("turmas:alunos_importar_multiturma")

        response = client_professor.post(url, {"arquivo_csv": arquivo})

        assert response.status_code == 200
        assert Aluno.objects.filter(email="ana.silva@escola.pr.gov.br").exists()
        assert Matricula.objects.filter(
            aluno__email="ana.silva@escola.pr.gov.br",
            turma=turma,
            ativa=True,
        ).exists()
        assert Matricula.objects.filter(
            aluno__email="bruno.lima@escola.pr.gov.br",
            turma=outra_turma,
            ativa=True,
        ).exists()
        assert response.context["report"]["sucesso"] == 2

    def test_importar_multiturma_csv_reativa_matricula_existente(
        self, client_professor, turma, aluno
    ):
        Matricula.objects.create(aluno=aluno, turma=turma, ativa=False)
        csv_reimport = (
            f"nome,email,matricula,turma\n{aluno.nome},{aluno.email},{aluno.matricula},{turma.nome}\n"
        ).encode("utf-8")
        arquivo = SimpleUploadedFile(
            "alunos-multiturma.csv",
            csv_reimport,
            content_type="text/csv",
        )
        url = reverse("turmas:alunos_importar_multiturma")

        response = client_professor.post(url, {"arquivo_csv": arquivo})

        assert response.status_code == 200
        assert Matricula.objects.get(aluno=aluno, turma=turma).ativa is True
        assert response.context["report"]["matriculas_reativadas"] == 1

    def test_importar_multiturma_csv_exibe_erro_para_turma_inexistente(
        self, client_professor
    ):
        arquivo = SimpleUploadedFile(
            "alunos-multiturma.csv",
            (
                "nome,email,matricula,turma\n"
                "Ana Silva,ana.silva@escola.pr.gov.br,1001,Turma Fantasma\n"
            ).encode("utf-8"),
            content_type="text/csv",
        )
        url = reverse("turmas:alunos_importar_multiturma")

        response = client_professor.post(url, {"arquivo_csv": arquivo})

        assert response.status_code == 200
        assert response.context["report"]["linhas_com_erro"] == 1
        assert "Turma Fantasma" in response.content.decode()

    def test_busca_htmx_filtra_por_nome(
        self, client_professor, turma, aluno, matricula
    ):
        outra = Aluno.objects.create(
            nome="Carlos Pereira",
            email="carlos.pereira@escola.pr.gov.br",
            matricula="3002",
        )
        Matricula.objects.create(aluno=outra, turma=turma, ativa=True)

        url = reverse("turmas:alunos_busca_htmx", kwargs={"pk": turma.pk})
        response = client_professor.get(url, {"q": "Carlos"})

        assert response.status_code == 200
        assert "Carlos Pereira" in response.content.decode()
        assert "João Silva" not in response.content.decode()

    def test_busca_htmx_retorna_tabela_completa_em_container_seguro(
        self, client_professor, turma, aluno, matricula
    ):
        url = reverse("turmas:alunos_busca_htmx", kwargs={"pk": turma.pk})

        response = client_professor.get(url, {"q": aluno.nome})
        html = response.content.decode()

        assert response.status_code == 200
        assert "<table" in html
        assert 'id="tabela-alunos-body"' in html
        assert "hover:bg-zinc-800/70" in html

    def test_mover_turma_altera_matricula(
        self, client_professor, turma, aluno, matricula, outra_turma
    ):
        url = reverse(
            "turmas:alunos_mover", kwargs={"pk": turma.pk, "aluno_pk": aluno.pk}
        )

        response = client_professor.post(url, {"nova_turma_pk": outra_turma.pk})

        assert response.status_code == 302
        matricula.refresh_from_db()
        assert matricula.turma == outra_turma

    def test_detalhe_aluno_fora_da_turma_retorna_404(
        self, client_professor, turma, outra_turma, aluno
    ):
        Matricula.objects.create(aluno=aluno, turma=outra_turma, ativa=True)
        url = reverse(
            "turmas:alunos_detalhe", kwargs={"pk": turma.pk, "aluno_pk": aluno.pk}
        )

        response = client_professor.get(url)

        assert response.status_code == 404

    def test_mover_turma_para_turma_inativa_retorna_404(
        self, client_professor, turma, aluno, matricula, db
    ):
        turma_inativa = Turma.objects.create(
            nome="Turma Inativa",
            codigo="INATIVA2024",
            descricao="Arquivada",
            periodo="1",
            ano_letivo=2024,
            ativa=False,
        )
        url = reverse(
            "turmas:alunos_mover", kwargs={"pk": turma.pk, "aluno_pk": aluno.pk}
        )

        response = client_professor.post(url, {"nova_turma_pk": turma_inativa.pk})

        assert response.status_code == 404


@pytest.mark.django_db
class TestAlunoSignals:
    def test_login_vincula_usuario_e_reativa_todas_as_matriculas(
        self, turma, outra_turma, aluno_user
    ):
        aluno = Aluno.objects.create(
            nome="Joao Silva",
            email=aluno_user.email,
            matricula="2024001",
        )
        Matricula.objects.create(aluno=aluno, turma=turma, ativa=False)
        Matricula.objects.create(aluno=aluno, turma=outra_turma, ativa=False)

        vincular_ou_criar_aluno_apos_login(
            sender=type(aluno_user),
            user=aluno_user,
            request=None,
        )

        aluno.refresh_from_db()
        assert aluno.user == aluno_user
        assert Matricula.objects.filter(aluno=aluno, ativa=True).count() == 2
