from django.views.generic import TemplateView

from core.mixins import ProfessorRequiredMixin


class DashboardView(ProfessorRequiredMixin, TemplateView):
    """Dashboard principal do professor — implementado na Sprint 4."""
    template_name = "core/dashboard.html"
