"""
Admin URL patterns for turmas and aulas.

Included in config/urls.py under path("painel/turmas/", ...).
Does NOT define app_name — the "turmas" namespace is provided by
turmas/urls.py (which has app_name = "turmas").

Names here are registered into the "turmas" namespace because
config/urls.py includes this module via:
    include(("turmas.admin_urls", "turmas"), namespace="turmas")
"""

from django.urls import path

from aulas import views as aulas_views

from . import views as turmas_views

urlpatterns = [
    # Turmas CRUD
    path("", turmas_views.TurmaListView.as_view(), name="lista"),
    path("nova/", turmas_views.TurmaCreateView.as_view(), name="nova"),
    path("<int:pk>/", turmas_views.TurmaDetailView.as_view(), name="detalhe"),
    path("<int:pk>/editar/", turmas_views.TurmaUpdateView.as_view(), name="editar"),
    path("<int:pk>/arquivar/", turmas_views.TurmaArquivarView.as_view(), name="arquivar"),
    # Aulas aninhadas sob a turma
    path("<int:pk>/aulas/", aulas_views.AulaListView.as_view(), name="aulas_lista"),
    path("<int:pk>/aulas/nova/", aulas_views.AulaCreateView.as_view(), name="aulas_nova"),
    path(
        "<int:pk>/aulas/reordenar/",
        aulas_views.AulaReordenarView.as_view(),
        name="aulas_reordenar",
    ),
    path(
        "<int:pk>/aulas/<int:aula_pk>/",
        aulas_views.AulaDetailView.as_view(),
        name="aulas_detalhe",
    ),
    path(
        "<int:pk>/aulas/<int:aula_pk>/editar/",
        aulas_views.AulaUpdateView.as_view(),
        name="aulas_editar",
    ),
    path(
        "<int:pk>/aulas/<int:aula_pk>/excluir/",
        aulas_views.AulaDeleteView.as_view(),
        name="aulas_excluir",
    ),
    path(
        "<int:pk>/aulas/<int:aula_pk>/realizada/",
        aulas_views.AulaMarcarRealizadaView.as_view(),
        name="aulas_realizada",
    ),
]
