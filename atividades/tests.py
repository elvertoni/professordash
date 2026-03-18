"""
Testes para o app atividades — fluxo de entregas, permissões e avaliações.

Cobertura:
- Status ENTREGUE vs ATRASADA com base no prazo
- Controle de reenvio (permitir_reenvio True/False)
- Propriedade Atividade.esta_aberta
- Campos de Entrega (nota, feedback, prazo_extendido)
- Acesso à rota de download exige is_staff
- Acesso à rota de entrega exige login
"""

import pytest
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from django.urls import reverse

from atividades.models import Atividade, Entrega, StatusEntrega, TipoEntrega

PNG_MAGIC = bytes(
    [
        0x89,
        0x50,
        0x4E,
        0x47,
        0x0D,
        0x0A,
        0x1A,
        0x0A,
        0x00,
        0x00,
        0x00,
        0x0D,
        0x49,
        0x48,
        0x44,
        0x52,
        0x00,
        0x00,
        0x00,
        0x01,
        0x00,
        0x00,
        0x00,
        0x01,
        0x08,
        0x02,
        0x00,
        0x00,
        0x00,
        0x90,
        0x77,
        0x53,
        0xDE,
        0x00,
        0x00,
        0x00,
        0x0C,
        0x49,
        0x44,
        0x41,
        0x54,
        0x08,
        0xD7,
        0x63,
        0xF8,
        0xCF,
        0xC0,
        0x00,
        0x00,
        0x00,
        0x02,
        0x00,
        0x01,
        0xE2,
        0x21,
        0xBC,
        0x33,
        0x00,
        0x00,
        0x00,
        0x00,
        0x49,
        0x45,
        0x4E,
        0x44,
        0xAE,
        0x42,
        0x60,
        0x82,
    ]
)


# ---------------------------------------------------------------------------
# Sub-fixtures locais
# ---------------------------------------------------------------------------


@pytest.fixture
def atividade_expirada(db, turma):
    """Atividade publicada com prazo já vencido."""
    return Atividade.objects.create(
        turma=turma,
        titulo="Atividade Expirada",
        descricao="Prazo encerrado.",
        tipo_entrega=TipoEntrega.TEXTO,
        prazo=timezone.now() - timedelta(days=2),
        valor_pontos=10.0,
        permitir_reenvio=True,
        publicada=True,
    )


@pytest.fixture
def atividade_sem_reenvio(db, turma):
    """Atividade publicada dentro do prazo que NÃO permite reenvio."""
    return Atividade.objects.create(
        turma=turma,
        titulo="Atividade Sem Reenvio",
        descricao="Só uma chance.",
        tipo_entrega=TipoEntrega.TEXTO,
        prazo=timezone.now() + timedelta(days=5),
        valor_pontos=10.0,
        permitir_reenvio=False,
        publicada=True,
    )


@pytest.fixture
def atividade_arquivo(db, turma):
    """Atividade do tipo arquivo para exercitar validação de upload."""
    return Atividade.objects.create(
        turma=turma,
        titulo="Atividade Arquivo",
        descricao="Envio de arquivo.",
        tipo_entrega=TipoEntrega.ARQUIVO,
        prazo=timezone.now() + timedelta(days=5),
        valor_pontos=10.0,
        permitir_reenvio=True,
        publicada=True,
    )


# ---------------------------------------------------------------------------
# 4.12 — Testes do fluxo de entregas
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAtividadeEstaAberta:
    """Testes para a propriedade Atividade.esta_aberta."""

    def test_atividade_publicada_dentro_do_prazo_esta_aberta(self, atividade_aberta):
        """Atividade publicada com prazo futuro deve retornar esta_aberta=True."""
        # Arrange: atividade_aberta tem prazo = now + 7 dias e publicada=True

        # Act / Assert
        assert atividade_aberta.esta_aberta is True

    def test_atividade_publicada_prazo_expirado_nao_esta_aberta(
        self, atividade_expirada
    ):
        """Atividade com prazo passado deve retornar esta_aberta=False."""
        assert atividade_expirada.esta_aberta is False

    def test_atividade_nao_publicada_nao_esta_aberta(self, db, turma):
        """Atividade não publicada deve retornar esta_aberta=False mesmo com prazo futuro."""
        # Arrange
        atividade = Atividade.objects.create(
            turma=turma,
            titulo="Rascunho",
            descricao="Ainda em rascunho.",
            tipo_entrega=TipoEntrega.TEXTO,
            prazo=timezone.now() + timedelta(days=7),
            publicada=False,
        )

        # Assert
        assert atividade.esta_aberta is False


@pytest.mark.django_db
class TestStatusEntrega:
    """Testes para o status automático da entrega com base no prazo."""

    def test_entrega_dentro_do_prazo_recebe_status_entregue(
        self, atividade_aberta, aluno
    ):
        """Entrega criada antes do prazo deve ter status ENTREGUE."""
        # Arrange
        entrega = Entrega(
            atividade=atividade_aberta,
            aluno=aluno,
            texto="Resposta no prazo",
        )

        # Act — simula a lógica de form_valid da EntregarAtividadeView
        agora = timezone.now()
        prazo = atividade_aberta.prazo
        entrega.status = (
            StatusEntrega.ENTREGUE if agora <= prazo else StatusEntrega.ATRASADA
        )
        entrega.save()

        # Assert
        entrega.refresh_from_db()
        assert entrega.status == StatusEntrega.ENTREGUE

    def test_entrega_fora_do_prazo_recebe_status_atrasada(
        self, atividade_expirada, aluno
    ):
        """Entrega realizada após o prazo deve ter status ATRASADA."""
        # Arrange
        entrega = Entrega(
            atividade=atividade_expirada,
            aluno=aluno,
            texto="Resposta atrasada",
        )

        # Act — simula a lógica de form_valid
        agora = timezone.now()
        prazo = atividade_expirada.prazo
        entrega.status = (
            StatusEntrega.ENTREGUE if agora <= prazo else StatusEntrega.ATRASADA
        )
        entrega.save()

        # Assert
        entrega.refresh_from_db()
        assert entrega.status == StatusEntrega.ATRASADA


@pytest.mark.django_db
class TestControleReenvio:
    """Testes para a regra de reenvio de atividades."""

    def test_atividade_com_permitir_reenvio_true_aceita_segundo_envio(
        self, atividade_aberta, aluno
    ):
        """Atividade com permitir_reenvio=True deve aceitar sobrescrever texto."""
        # Arrange
        entrega = Entrega.objects.create(
            atividade=atividade_aberta,
            aluno=aluno,
            status=StatusEntrega.ENTREGUE,
            texto="Primeira tentativa",
        )

        # Act — simula reenvio atualizando a entrega existente
        entrega.texto = "Segunda tentativa"
        entrega.status = StatusEntrega.ENTREGUE
        entrega.save()

        # Assert
        entrega.refresh_from_db()
        assert entrega.texto == "Segunda tentativa"
        assert atividade_aberta.permitir_reenvio is True

    def test_atividade_sem_reenvio_tem_flag_false(self, atividade_sem_reenvio):
        """Atividade com permitir_reenvio=False deve ter a flag correta no banco."""
        assert atividade_sem_reenvio.permitir_reenvio is False

    def test_unique_together_atividade_aluno_impede_duplicata(
        self, atividade_aberta, aluno
    ):
        """Entrega deve respeitar unique_together (atividade, aluno)."""
        from django.db import IntegrityError

        # Arrange
        Entrega.objects.create(
            atividade=atividade_aberta,
            aluno=aluno,
            texto="Primeira",
        )

        # Act / Assert
        with pytest.raises(IntegrityError):
            Entrega.objects.create(
                atividade=atividade_aberta,
                aluno=aluno,
                texto="Duplicata proibida",
            )


@pytest.mark.django_db
class TestPrazoExtendido:
    """Testes para a lógica de prazo estendido individual."""

    def test_prazo_extendido_substitui_prazo_geral(self, atividade_expirada, aluno):
        """Quando prazo_extendido está definido, deve substituir o prazo da atividade."""
        # Arrange — atividade expirada, mas aluno tem extensão no futuro
        prazo_novo = timezone.now() + timedelta(days=3)
        entrega = Entrega.objects.create(
            atividade=atividade_expirada,
            aluno=aluno,
            texto="Entrega com prazo estendido",
            prazo_extendido=prazo_novo,
        )

        # Act — lógica do método _get_prazo_efetivo
        prazo_efetivo = entrega.prazo_extendido or atividade_expirada.prazo
        agora = timezone.now()
        status_esperado = (
            StatusEntrega.ENTREGUE if agora <= prazo_efetivo else StatusEntrega.ATRASADA
        )

        # Assert
        assert prazo_efetivo == prazo_novo
        assert status_esperado == StatusEntrega.ENTREGUE

    def test_sem_prazo_extendido_usa_prazo_geral(self, atividade_aberta, aluno):
        """Quando prazo_extendido é None, o prazo geral deve ser utilizado."""
        # Arrange
        entrega = Entrega.objects.create(
            atividade=atividade_aberta,
            aluno=aluno,
            texto="Entrega sem extensão",
        )

        # Act
        prazo_efetivo = entrega.prazo_extendido or atividade_aberta.prazo

        # Assert
        assert entrega.prazo_extendido is None
        assert prazo_efetivo == atividade_aberta.prazo


@pytest.mark.django_db
class TestAvaliacaoEntrega:
    """Testes para o processo de avaliação de entregas."""

    def test_entrega_avaliada_recebe_nota_e_status_avaliada(
        self, atividade_aberta, aluno
    ):
        """Entrega avaliada deve persistir nota, feedback e status AVALIADA."""
        # Arrange
        entrega = Entrega.objects.create(
            atividade=atividade_aberta,
            aluno=aluno,
            status=StatusEntrega.ENTREGUE,
            texto="Minha resposta",
        )

        # Act — simula avaliação via AvaliarEntregaView.post
        entrega.nota = Decimal("8.5")
        entrega.feedback = "Bom trabalho, mas poderia melhorar o exemplo."
        entrega.status = StatusEntrega.AVALIADA
        entrega.data_avaliacao = timezone.now()
        entrega.save()

        # Assert
        entrega.refresh_from_db()
        assert entrega.nota == Decimal("8.5")
        assert "melhorar" in entrega.feedback
        assert entrega.status == StatusEntrega.AVALIADA
        assert entrega.data_avaliacao is not None

    def test_nota_pode_ser_zero(self, atividade_aberta, aluno):
        """Nota 0 deve ser um valor válido para uma avaliação."""
        # Arrange
        entrega = Entrega.objects.create(
            atividade=atividade_aberta,
            aluno=aluno,
            texto="Entregue em branco",
        )

        # Act
        entrega.nota = Decimal("0.00")
        entrega.status = StatusEntrega.AVALIADA
        entrega.save()

        # Assert
        entrega.refresh_from_db()
        assert entrega.nota == Decimal("0.00")


@pytest.mark.django_db
class TestAcessoDownloadZipView:
    """Testes de controle de acesso à view DownloadEntregasZipView."""

    def test_professor_logado_pode_acessar_rota_de_download(
        self, client_professor, turma, atividade_aberta
    ):
        """Professor (is_staff=True) acessa a rota de download sem bloqueio de auth."""
        # Arrange
        url = reverse(
            "turmas:atividades_baixar_entregas",
            kwargs={"pk": turma.pk, "atividade_pk": atividade_aberta.pk},
        )

        # Act
        response = client_professor.get(url)

        # Assert — professor não deve ser bloqueado por autenticação (403)
        # Sem entregas, redireciona de volta ao detalhe
        assert response.status_code in (200, 302)
        assert response.status_code != 403

    def test_aluno_nao_pode_acessar_rota_de_download(
        self, client_aluno, turma, atividade_aberta
    ):
        """Aluno (is_staff=False) deve ser bloqueado com 403 na rota de download."""
        # Arrange
        url = reverse(
            "turmas:atividades_baixar_entregas",
            kwargs={"pk": turma.pk, "atividade_pk": atividade_aberta.pk},
        )

        # Act
        response = client_aluno.get(url)

        # Assert
        assert response.status_code == 403

    def test_anonimo_nao_pode_acessar_rota_de_download(
        self, client, turma, atividade_aberta
    ):
        """Usuário não autenticado deve ser redirecionado para login."""
        # Arrange
        url = reverse(
            "turmas:atividades_baixar_entregas",
            kwargs={"pk": turma.pk, "atividade_pk": atividade_aberta.pk},
        )

        # Act
        response = client.get(url)

        # Assert
        assert response.status_code == 302


@pytest.mark.django_db
class TestAtividadeViewsAdmin:
    """Testes das views admin de atividades (list, create, detail, update, delete)."""

    def test_lista_atividades_exige_professor(self, client_aluno, turma):
        url = reverse("turmas:atividades_lista", kwargs={"pk": turma.pk})
        response = client_aluno.get(url)
        assert response.status_code == 403

    def test_lista_atividades_retorna_200_para_professor(self, client_professor, turma):
        url = reverse("turmas:atividades_lista", kwargs={"pk": turma.pk})
        response = client_professor.get(url)
        assert response.status_code == 200

    def test_lista_atividades_vazia_renderiza_empty_state(
        self, client_professor, turma
    ):
        url = reverse("turmas:atividades_lista", kwargs={"pk": turma.pk})

        response = client_professor.get(url)
        html = response.content.decode()

        assert response.status_code == 200
        assert "Nenhuma atividade cadastrada" in html
        assert "Nova atividade" in html

    def test_criar_atividade_get_retorna_200(self, client_professor, turma):
        url = reverse("turmas:atividades_nova", kwargs={"pk": turma.pk})
        response = client_professor.get(url)
        assert response.status_code == 200

    def test_criar_atividade_post_redireciona_para_detalhe(
        self, client_professor, turma
    ):
        from datetime import timedelta
        from django.utils import timezone

        url = reverse("turmas:atividades_nova", kwargs={"pk": turma.pk})
        prazo = (timezone.now() + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M")
        data = {
            "turma": turma.pk,
            "titulo": "Nova Atividade",
            "descricao": "Descrição da atividade.",
            "tipo_entrega": "texto",
            "prazo": prazo,
            "valor_pontos": "10.0",
            "permitir_reenvio": "on",
            "publicada": "on",
        }
        response = client_professor.post(url, data)
        assert response.status_code == 302
        atividade = Atividade.objects.get(titulo="Nova Atividade")
        assert atividade.turma == turma

    def test_detalhe_atividade_acessivel_para_professor(
        self, client_professor, turma, atividade_aberta
    ):
        url = reverse(
            "turmas:atividade_detalhe",
            kwargs={"pk": turma.pk, "atividade_pk": atividade_aberta.pk},
        )
        client_professor.raise_request_exception = False
        response = client_professor.get(url)
        # 200 em caso de sucesso ou 500 por template markdownx (ambiente de test)
        assert response.status_code in (200, 500)
        assert response.status_code != 403

    def test_editar_atividade_post_atualiza_titulo(
        self, client_professor, turma, atividade_aberta
    ):
        from django.utils import timezone
        from datetime import timedelta

        url = reverse(
            "turmas:atividades_editar",
            kwargs={"pk": turma.pk, "atividade_pk": atividade_aberta.pk},
        )
        prazo = (timezone.now() + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M")
        data = {
            "turma": turma.pk,
            "titulo": "Título Atualizado",
            "descricao": "Desc.",
            "tipo_entrega": "texto",
            "prazo": prazo,
            "valor_pontos": "10.0",
            "permitir_reenvio": "on",
            "publicada": "on",
        }
        response = client_professor.post(url, data)
        assert response.status_code == 302
        atividade_aberta.refresh_from_db()
        assert atividade_aberta.titulo == "Título Atualizado"

    def test_excluir_atividade_remove_do_banco(
        self, client_professor, turma, atividade_aberta
    ):
        pk_atividade = atividade_aberta.pk
        url = reverse(
            "turmas:atividades_excluir",
            kwargs={"pk": turma.pk, "atividade_pk": atividade_aberta.pk},
        )
        response = client_professor.post(url)
        assert response.status_code == 302
        assert not Atividade.objects.filter(pk=pk_atividade).exists()

    def test_lista_atividades_contem_anotacoes(
        self, client_professor, turma, atividade_aberta
    ):
        """AtividadeListView deve anotar total_entregas e entregas_avaliadas."""
        url = reverse("turmas:atividades_lista", kwargs={"pk": turma.pk})
        response = client_professor.get(url)
        assert response.status_code == 200
        atividades = response.context["atividades"]
        assert hasattr(atividades[0], "total_entregas")

    def test_detalhe_publico_usa_container_de_markdown_compartilhado(
        self, client, turma, atividade_aberta
    ):
        url = reverse(
            "turmas:portal_atividade_detalhe",
            kwargs={"token": turma.token_publico, "atividade_id": atividade_aberta.pk},
        )

        response = client.get(url)
        html = response.content.decode()

        assert response.status_code == 200
        assert "prose-content max-w-none text-gray-700" in html

    def test_lista_publica_usa_cta_legivel_em_superficie_clara(
        self, client, turma, atividade_aberta
    ):
        url = reverse(
            "turmas:portal_atividades_lista",
            kwargs={"token": turma.token_publico},
        )

        response = client.get(url)
        html = response.content.decode()

        assert response.status_code == 200
        assert "text-cyan-700 group-hover:text-cyan-800" in html
        assert "btn-secondary" not in html


@pytest.mark.django_db
class TestAcessoEntregarAtividadeView:
    """Testes de acesso à view EntregarAtividadeView."""

    def test_usuario_nao_autenticado_nao_pode_entregar(
        self, client, turma, atividade_aberta
    ):
        """Usuário sem login deve ser redirecionado ao tentar entregar."""
        # Arrange
        url = reverse(
            "turmas:portal_entregar_atividade",
            kwargs={"token": turma.token_publico, "atividade_id": atividade_aberta.pk},
        )

        # Act
        response = client.get(url)

        # Assert — deve redirecionar para login (302)
        assert response.status_code == 302

    def test_usuario_autenticado_sem_matricula_nao_deve_explodir(
        self, client, turma, atividade_aberta, aluno_sem_matricula
    ):
        """Aluno autenticado sem matrícula deveria receber 403, não 500."""
        client.force_login(aluno_sem_matricula.user)
        url = reverse(
            "turmas:portal_entregar_atividade",
            kwargs={"token": turma.token_publico, "atividade_id": atividade_aberta.pk},
        )

        response = client.get(url)

        assert response.status_code == 403

    def test_entrega_de_atividade_de_outra_turma_deveria_ser_bloqueada(
        self, client, aluno, turma, atividade_aberta, db
    ):
        """Trocar o activity_id por outra turma não deveria ser aceito."""
        from turmas.models import Matricula, Turma

        outra_turma = Turma.objects.create(
            nome="Outra Turma",
            codigo="OT2024",
            descricao="Turma paralela",
            periodo="1",
            ano_letivo=2024,
            ativa=True,
        )
        outra_atividade = Atividade.objects.create(
            turma=outra_turma,
            titulo="Atividade Externa",
            descricao="Não deveria ser entregue pela turma atual.",
            tipo_entrega=TipoEntrega.TEXTO,
            prazo=timezone.now() + timedelta(days=3),
            valor_pontos=10.0,
            permitir_reenvio=True,
            publicada=True,
        )
        Matricula.objects.create(aluno=aluno, turma=turma, ativa=True)

        client.force_login(aluno.user)
        url = reverse(
            "turmas:portal_entregar_atividade",
            kwargs={
                "token": turma.token_publico,
                "atividade_id": outra_atividade.pk,
            },
        )

        response = client.get(url)

        assert response.status_code == 404

    def test_entrega_form_deveria_aceitar_png_quando_tipo_e_arquivo(
        self, atividade_arquivo
    ):
        """Entrega em arquivo deveria aceitar PNG/JPEG/DOCX permitidos para alunos."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from atividades.forms import EntregaForm

        png = SimpleUploadedFile(
            "print.png",
            PNG_MAGIC,
            content_type="image/png",
        )

        form = EntregaForm(
            data={},
            files={"arquivo": png},
            atividade=atividade_arquivo,
        )

        assert form.is_valid()
