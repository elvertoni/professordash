"""
URL configuration centralizada para o app turmas.

Incluída em config/urls.py sem prefixo:
    path("", include("turmas.urls"))

Os prefixos /painel/turmas/ e /turma/ ficam definidos aqui diretamente,
garantindo que reverse() sempre funcione com um único namespace "turmas".
"""

from django.urls import path

from aulas import views as aulas_views
from materiais import views as materiais_views
from alunos import views as alunos_views
from atividades import views as atividades_views

from . import views as turmas_views

app_name = "turmas"

urlpatterns = [
    # ------------------------------------------------------------------
    # Admin (/painel/turmas/...)
    # ------------------------------------------------------------------
    path("painel/turmas/", turmas_views.TurmaListView.as_view(), name="lista"),
    path("painel/turmas/nova/", turmas_views.TurmaCreateView.as_view(), name="nova"),
    path(
        "painel/turmas/<int:pk>/",
        turmas_views.TurmaDetailView.as_view(),
        name="detalhe",
    ),
    path(
        "painel/turmas/<int:pk>/editar/",
        turmas_views.TurmaUpdateView.as_view(),
        name="editar",
    ),
    path(
        "painel/turmas/<int:pk>/arquivar/",
        turmas_views.TurmaArquivarView.as_view(),
        name="arquivar",
    ),
    path(
        "painel/turmas/<int:pk>/excluir/",
        turmas_views.TurmaDeleteView.as_view(),
        name="excluir",
    ),
    # Aulas admin
    path(
        "painel/turmas/<int:pk>/aulas/",
        aulas_views.AulaListView.as_view(),
        name="aulas_lista",
    ),
    path(
        "painel/turmas/<int:pk>/aulas/nova/",
        aulas_views.AulaCreateView.as_view(),
        name="aulas_nova",
    ),
    path(
        "painel/turmas/<int:pk>/aulas/importar-md/",
        aulas_views.AulaImportarMdView.as_view(),
        name="aulas_importar_md",
    ),
    path(
        "painel/turmas/<int:pk>/aulas/reordenar/",
        aulas_views.AulaReordenarView.as_view(),
        name="aulas_reordenar",
    ),
    path(
        "painel/turmas/<int:pk>/aulas/<int:aula_pk>/",
        aulas_views.AulaDetailView.as_view(),
        name="aulas_detalhe",
    ),
    path(
        "painel/turmas/<int:pk>/aulas/<int:aula_pk>/editar/",
        aulas_views.AulaUpdateView.as_view(),
        name="aulas_editar",
    ),
    path(
        "painel/turmas/<int:pk>/aulas/<int:aula_pk>/excluir/",
        aulas_views.AulaDeleteView.as_view(),
        name="aulas_excluir",
    ),
    path(
        "painel/turmas/<int:pk>/aulas/<int:aula_pk>/realizada/",
        aulas_views.AulaMarcarRealizadaView.as_view(),
        name="aulas_realizada",
    ),
    # Materiais admin
    path(
        "painel/turmas/<int:pk>/materiais/",
        materiais_views.MaterialListView.as_view(),
        name="materiais_lista",
    ),
    path(
        "painel/turmas/<int:pk>/materiais/novo/",
        materiais_views.MaterialCreateView.as_view(),
        name="materiais_novo",
    ),
    path(
        "painel/turmas/<int:pk>/materiais/<int:material_pk>/editar/",
        materiais_views.MaterialUpdateView.as_view(),
        name="materiais_editar",
    ),
    path(
        "painel/turmas/<int:pk>/materiais/<int:material_pk>/download/",
        materiais_views.MaterialDownloadAdminView.as_view(),
        name="materiais_download_admin",
    ),
    path(
        "painel/turmas/<int:pk>/materiais/<int:material_pk>/excluir/",
        materiais_views.MaterialDeleteView.as_view(),
        name="materiais_excluir",
    ),
    # Atividades admin
    path(
        "painel/turmas/<int:pk>/atividades/",
        atividades_views.AtividadeListView.as_view(),
        name="atividades_lista",
    ),
    path(
        "painel/turmas/<int:pk>/atividades/nova/",
        atividades_views.AtividadeCreateView.as_view(),
        name="atividades_nova",
    ),
    path(
        "painel/turmas/<int:pk>/atividades/<int:atividade_pk>/",
        atividades_views.AtividadeDetailView.as_view(),
        name="atividade_detalhe",
    ),
    path(
        "painel/turmas/<int:pk>/atividades/<int:atividade_pk>/baixar-entregas/",
        atividades_views.DownloadEntregasZipView.as_view(),
        name="atividades_baixar_entregas",
    ),
    path(
        "painel/turmas/<int:pk>/atividades/<int:atividade_pk>/entregas/<int:entrega_pk>/arquivo/",
        atividades_views.DownloadEntregaArquivoProfessorView.as_view(),
        name="atividades_download_entrega_admin",
    ),
    path(
        "painel/turmas/<int:pk>/atividades/<int:atividade_pk>/entregas/<int:entrega_pk>/avaliar/",
        atividades_views.AvaliarEntregaView.as_view(),
        name="atividades_avaliar_entrega",
    ),
    path(
        "painel/turmas/<int:pk>/atividades/<int:atividade_pk>/editar/",
        atividades_views.AtividadeUpdateView.as_view(),
        name="atividades_editar",
    ),
    path(
        "painel/turmas/<int:pk>/atividades/<int:atividade_pk>/excluir/",
        atividades_views.AtividadeDeleteView.as_view(),
        name="atividades_excluir",
    ),
    path(
        "painel/turmas/<int:pk>/atividades/<int:atividade_pk>/alunos/<int:aluno_pk>/reabrir-prazo/",
        atividades_views.ReabrirPrazoAlunoView.as_view(),
        name="atividades_reabrir_prazo",
    ),
    # Alunos admin
    path(
        "painel/turmas/<int:pk>/alunos/",
        alunos_views.AlunoListView.as_view(),
        name="alunos_lista",
    ),
    path(
        "painel/turmas/<int:pk>/alunos/novo/",
        alunos_views.AlunoCreateView.as_view(),
        name="alunos_novo",
    ),
    path(
        "painel/turmas/<int:pk>/alunos/importar/",
        alunos_views.AlunoImportarCSVView.as_view(),
        name="alunos_importar",
    ),
    path(
        "painel/turmas/<int:pk>/alunos/htmx/busca/",
        alunos_views.AlunosBuscaHTMXView.as_view(),
        name="alunos_busca_htmx",
    ),
    path(
        "painel/turmas/<int:pk>/alunos/<int:aluno_pk>/",
        alunos_views.AlunoDetailView.as_view(),
        name="alunos_detalhe",
    ),
    path(
        "painel/turmas/<int:pk>/alunos/<int:aluno_pk>/remover/",
        alunos_views.AlunoRemoverView.as_view(),
        name="alunos_remover",
    ),
    # Boletim
    path(
        "painel/turmas/<int:pk>/boletim/",
        turmas_views.BoletimTurmaView.as_view(),
        name="boletim_turma",
    ),
    path(
        "painel/turmas/<int:pk>/boletim/exportar/csv/",
        turmas_views.ExportarBoletimCSVView.as_view(),
        name="boletim_exportar_csv",
    ),
    path(
        "painel/turmas/<int:pk>/boletim/exportar/pdf/",
        turmas_views.ExportarBoletimPDFView.as_view(),
        name="boletim_exportar_pdf",
    ),
    path(
        "painel/turmas/<int:pk>/alunos/<int:aluno_pk>/editar/",
        alunos_views.AlunoUpdateView.as_view(),
        name="alunos_editar",
    ),
    path(
        "painel/turmas/<int:pk>/alunos/<int:aluno_pk>/mover/",
        alunos_views.AlunoMoverTurmaView.as_view(),
        name="alunos_mover",
    ),
    # ------------------------------------------------------------------
    # Portal público (/turma/<uuid:token>/...)
    # ------------------------------------------------------------------
    path(
        "turma/<uuid:token>/",
        turmas_views.TurmaPortalPublicoView.as_view(),
        name="portal",
    ),
    path(
        "turma/<uuid:token>/entrar/",
        turmas_views.TurmaEntrarView.as_view(),
        name="entrar",
    ),
    path(
        "turma/<uuid:token>/minha-area/",
        alunos_views.MinhaAreaView.as_view(),
        name="portal_minha_area",
    ),
    path(
        "turma/<uuid:token>/minhas-notas/",
        turmas_views.MinhasNotasView.as_view(),
        name="portal_minhas_notas",
    ),
    path(
        "turma/<uuid:token>/aulas/",
        aulas_views.AulaListaPublicaView.as_view(),
        name="portal_aulas_lista",
    ),
    path(
        "turma/<uuid:token>/aulas/<int:aula_pk>/",
        aulas_views.AulaDetalhePublicoView.as_view(),
        name="portal_aulas_detalhe",
    ),
    path(
        "turma/<uuid:token>/materiais/",
        materiais_views.MaterialListaPublicaView.as_view(),
        name="portal_materiais_lista",
    ),
    path(
        "turma/<uuid:token>/materiais/<int:material_pk>/download/",
        materiais_views.MaterialDownloadPublicoView.as_view(),
        name="portal_materiais_download",
    ),
    path(
        "turma/<uuid:token>/atividades/",
        atividades_views.AtividadeListaPublicaView.as_view(),
        name="portal_atividades_lista",
    ),
    path(
        "turma/<uuid:token>/atividades/<int:atividade_id>/",
        atividades_views.AtividadeDetalhePublicoView.as_view(),
        name="portal_atividade_detalhe",
    ),
    path(
        "turma/<uuid:token>/atividades/<int:atividade_id>/entregar/",
        atividades_views.EntregarAtividadeView.as_view(),
        name="portal_entregar_atividade",
    ),
    path(
        "turma/<uuid:token>/entregas/<int:entrega_pk>/arquivo/",
        atividades_views.DownloadMinhaEntregaArquivoView.as_view(),
        name="portal_entrega_arquivo",
    ),
]
