from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # Autenticação local (professor)
    path("entrar/", include("django.contrib.auth.urls")),

    # Google OAuth (django-allauth)
    path("accounts/", include("allauth.urls")),

    # Markdownx (preview de campos markdown)
    path("markdownx/", include("markdownx.urls")),

    # Dashboard do professor
    path("painel/", include("core.urls")),

    # Todas as URLs de turmas e aulas (admin + portal público) num único include.
    # Os prefixos /painel/turmas/ e /turma/ estão definidos dentro de turmas/urls.py,
    # garantindo um único namespace "turmas" sem ambiguidade.
    path("", include("turmas.urls")),

    # Raiz → painel
    path("", RedirectView.as_view(url="/painel/", permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
