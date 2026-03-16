from django.db.models import Avg, Count, Q
from django.utils import timezone
from django.views.generic import TemplateView

from core.mixins import ProfessorRequiredMixin


class DashboardView(ProfessorRequiredMixin, TemplateView):
    """Dashboard principal do professor com KPIs, alertas e feeds."""

    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from turmas.models import Turma
        from atividades.models import Atividade, Entrega

        agora = timezone.now()
        turmas_ativas = Turma.objects.filter(ativa=True)

        # ── KPIs ──────────────────────────────────────────────────────────────
        ctx["kpi_turmas"] = turmas_ativas.count()
        ctx["kpi_alunos"] = (
            turmas_ativas
            .annotate(n=Count("alunos", distinct=True))
            .aggregate(total=Count("alunos", distinct=True))["total"]
        ) or 0
        ctx["kpi_atividades_abertas"] = Atividade.objects.filter(
            turma__ativa=True,
            publicada=True,
            prazo__gte=agora,
        ).count()
        ctx["kpi_entregas_pendentes"] = Entrega.objects.filter(
            atividade__turma__ativa=True,
            status__in=["entregue", "atrasada"],
            nota__isnull=True,
        ).count()

        # ── Alertas (task 4.4) ────────────────────────────────────────────────
        limite_prazo = agora + timezone.timedelta(hours=48)
        ctx["alertas_prazo"] = Atividade.objects.filter(
            turma__ativa=True,
            publicada=True,
            prazo__gte=agora,
            prazo__lte=limite_prazo,
        ).select_related("turma").order_by("prazo")[:5]

        ctx["alertas_avaliacao"] = Entrega.objects.filter(
            atividade__turma__ativa=True,
            status__in=["entregue", "atrasada"],
            nota__isnull=True,
        ).select_related("aluno", "atividade__turma").order_by("-data_envio")[:8]

        return ctx


class FeedEntregasView(ProfessorRequiredMixin, TemplateView):
    """Fragment HTMX: últimas entregas nas últimas 24h."""

    template_name = "core/_feed_entregas.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from atividades.models import Entrega

        inicio = timezone.now() - timezone.timedelta(hours=24)
        ctx["entregas_recentes"] = (
            Entrega.objects
            .filter(
                atividade__turma__ativa=True,
                data_envio__gte=inicio,
            )
            .select_related("aluno", "atividade", "atividade__turma")
            .order_by("-data_envio")[:15]
        )
        return ctx


class StatsTurmasView(ProfessorRequiredMixin, TemplateView):
    """Fragment HTMX: estatísticas por turma (taxa de entrega e média)."""

    template_name = "core/_stats_turmas.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from turmas.models import Turma
        from atividades.models import Entrega

        turmas = Turma.objects.filter(ativa=True).prefetch_related("alunos", "atividades")
        stats = []
        for turma in turmas:
            total_alunos = turma.alunos.count()
            total_atividades = turma.atividades.filter(publicada=True).count()
            total_entregas = Entrega.objects.filter(
                atividade__turma=turma,
                status__in=["entregue", "atrasada", "avaliada"],
            ).count()
            media = Entrega.objects.filter(
                atividade__turma=turma,
                nota__isnull=False,
            ).aggregate(m=Avg("nota"))["m"]

            # Taxa = entregas feitas / (alunos × atividades publicadas)
            total_esperado = total_alunos * total_atividades
            taxa = round((total_entregas / total_esperado) * 100) if total_esperado > 0 else 0

            stats.append({
                "turma": turma,
                "total_alunos": total_alunos,
                "total_atividades": total_atividades,
                "taxa_entrega": taxa,
                "media_notas": round(float(media), 1) if media else None,
            })

        ctx["stats_turmas"] = stats
        return ctx
