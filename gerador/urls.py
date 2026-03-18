from django.urls import path

from . import views

app_name = "gerador"

urlpatterns = [
    # Tela principal
    path("", views.GeradorIndexView.as_view(), name="index"),

    # Upload e criação da sessão
    path("upload/", views.UploadMaterialView.as_view(), name="upload"),

    # Planejamento (Modo Livre)
    path("planejar/", views.PlanejarView.as_view(), name="planejar_post"),
    path("<int:sessao_id>/planejar/", views.PlanejarView.as_view(), name="planejar"),

    # Aprovação do planejamento
    path("<int:sessao_id>/aprovar/", views.AprovarPlanejamentoView.as_view(), name="aprovar"),

    # Geração com SSE
    path("<int:sessao_id>/gerar/", views.GerarAulasView.as_view(), name="gerar"),

    # Preview da aula N
    path("<int:sessao_id>/preview/<int:numero>/", views.PreviewAulaView.as_view(), name="preview"),

    # Salvar/publicar rascunhos
    path("<int:sessao_id>/salvar/", views.SalvarAulasView.as_view(), name="salvar"),

    # Histórico de sessões
    path("historico/", views.HistoricoView.as_view(), name="historico"),
]
