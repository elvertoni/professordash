"""
URL configuration centralizada para o app turmas.

Incluída em config/urls.py sem prefixo:
    path("", include("turmas.urls"))

Os prefixos /painel/turmas/ e /turma/ ficam definidos aqui diretamente,
garantindo que reverse() sempre funcione com um único namespace "turmas".
"""

from django.urls import path

from aulas import views as aulas_views

from . import views as turmas_views

app_name = "turmas"

urlpatterns = [
    # ------------------------------------------------------------------
    # Admin (/painel/turmas/...)
    # ------------------------------------------------------------------
    path("painel/turmas/", turmas_views.TurmaListView.as_view(), name="lista"),
    path("painel/turmas/nova/", turmas_views.TurmaCreateView.as_view(), name="nova"),
    path("painel/turmas/<int:pk>/", turmas_views.TurmaDetailView.as_view(), name="detalhe"),
    path("painel/turmas/<int:pk>/editar/", turmas_views.TurmaUpdateView.as_view(), name="editar"),
    path(
        "painel/turmas/<int:pk>/arquivar/",
        turmas_views.TurmaArquivarView.as_view(),
        name="arquivar",
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
    # ------------------------------------------------------------------
    # Portal público (/turma/<uuid:token>/...)
    # ------------------------------------------------------------------
    path("turma/<uuid:token>/", turmas_views.TurmaPortalPublicoView.as_view(), name="portal"),
    path(
        "turma/<uuid:token>/entrar/",
        turmas_views.TurmaEntrarView.as_view(),
        name="entrar",
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
]
