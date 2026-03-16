from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from core.mixins import ProfessorRequiredMixin
from turmas.models import Turma
from .forms import AtividadeForm, AvaliacaoForm, EntregaForm, ReabrirPrazoForm
from .models import Atividade, Entrega


class AtividadeMixin(ProfessorRequiredMixin):
    """Mixin base para views de atividades do professor."""

    model = Atividade

    def get_turma(self):
        return get_object_or_404(Turma, id=self.kwargs.get("pk"))

    def get_queryset(self):
        """Professor só vê atividades de suas turmas."""
        turma = self.get_turma()
        return super().get_queryset().filter(turma=turma)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["turma"] = self.get_turma()
        return context


class AtividadeListView(AtividadeMixin, ListView):
    template_name = "atividades/lista.html"
    context_object_name = "atividades"
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(
            total_entregas=Count("entregas"),
            entregas_avaliadas=Count("entregas", filter=Q(entregas__status="avaliada"))
        )


class AtividadeCreateView(AtividadeMixin, CreateView):
    form_class = AtividadeForm
    template_name = "atividades/form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["turma_id"] = self.kwargs.get("pk")
        return kwargs

    def get_success_url(self):
        messages.success(self.request, "Atividade criada com sucesso!")
        return reverse("turmas:atividade_detalhe", kwargs={"pk": self.kwargs.get("pk"), "atividade_pk": self.object.pk})


class AtividadeUpdateView(AtividadeMixin, UpdateView):
    form_class = AtividadeForm
    template_name = "atividades/form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["turma_id"] = self.kwargs.get("pk")
        return kwargs

    def get_success_url(self):
        messages.success(self.request, "Atividade atualizada com sucesso!")
        return reverse("turmas:atividade_detalhe", kwargs={"pk": self.kwargs.get("pk"), "atividade_pk": self.object.pk})


class AtividadeDeleteView(AtividadeMixin, DeleteView):
    template_name = "atividades/confirmar_exclusao.html"

    def get_success_url(self):
        messages.success(self.request, "Atividade excluída com sucesso!")
        return reverse("turmas:detalhe", kwargs={"pk": self.kwargs.get("pk")})


class AtividadeDetailView(AtividadeMixin, DetailView):
    template_name = "atividades/detalhe.html"
    context_object_name = "atividade"
    paginate_entregas_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        atividade = self.get_object()

        # Alunos da turma
        alunos_turma = self.get_turma().alunos.all()

        # Entregas feitas
        entregas_qs = atividade.entregas.select_related("aluno").all()
        alunos_com_entrega = entregas_qs.values_list("aluno_id", flat=True)

        # Alunos que não entregaram
        alunos_sem_entrega = alunos_turma.exclude(id__in=alunos_com_entrega)

        # Paginação das entregas
        from django.core.paginator import Paginator
        paginator = Paginator(entregas_qs, self.paginate_entregas_by)
        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        context["entregas"] = page_obj
        context["entregas_page_obj"] = page_obj
        context["alunos_sem_entrega"] = alunos_sem_entrega
        return context


from django.utils import timezone
from core.mixins import AlunoAutenticadoMixin

class EntregarAtividadeView(AlunoAutenticadoMixin, UpdateView):
    """
    View para o aluno enviar ou atualizar sua entrega.
    Usamos UpdateView porque o aluno pode estar enviando pela primeira vez (criando)
    ou reenviando (atualizando) a entrega já existente.
    """
    model = Entrega
    form_class = EntregaForm
    template_name = "atividades/entregar.html"

    def get_object(self, queryset=None):
        """Retorna a entrega existente ou cria uma instância não salva se for o primeiro envio."""
        atividade_id = self.kwargs.get("atividade_id")
        self.atividade = get_object_or_404(Atividade, id=atividade_id, publicada=True)
        # self.matricula é setado pelo AlunoAutenticadoMixin (verifica matrícula ativa)
        aluno = self.matricula.aluno

        entrega, created = Entrega.objects.get_or_create(
            atividade=self.atividade,
            aluno=aluno,
            defaults={"status": "pendente"}
        )
        return entrega

    def dispatch(self, request, *args, **kwargs):
        # Primeiro pega o objeto para ter a self.atividade e a entrega
        response = super().dispatch(request, *args, **kwargs)
        
        # Só precisamos checar prazo se estiver tentando enviar (POST)
        if request.method == "POST":
            # Já tem uma entrega anterior e a atividade não permite reenvio?
            entrega = self.get_object()
            if entrega.pk and entrega.status in ["entregue", "atrasada", "avaliada"] and not self.atividade.permitir_reenvio:
                messages.error(request, "Esta atividade não permite reenvios.")
                return redirect("turmas:portal_minha_area", token=self.atividade.turma.token_publico)
        
        return response

    def _get_prazo_efetivo(self, entrega):
        """Retorna o prazo efetivo: individual se definido, senão o geral da atividade."""
        return entrega.prazo_extendido or self.atividade.prazo

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["atividade"] = self.atividade
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["atividade"] = self.atividade
        context["turma"] = self.atividade.turma
        return context

    def form_valid(self, form):
        entrega = form.save(commit=False)
        
        # Determina o status com base no prazo efetivo (individual ou geral)
        agora = timezone.now()
        prazo = self._get_prazo_efetivo(entrega)
        if agora <= prazo:
            entrega.status = "entregue"
        else:
            entrega.status = "atrasada"
            
        entrega.data_envio = agora
        entrega.save()
        
        messages.success(self.request, f"Atividade entregue com sucesso! Status: {entrega.get_status_display()}")
        return redirect("turmas:portal_minha_area", token=self.atividade.turma.token_publico)


import zipfile
import io
from django.http import HttpResponse
from django.utils.text import slugify
from django.views import View

class DownloadEntregasZipView(AtividadeMixin, View):
    """
    View para o professor baixar um arquivo .zip contendo
    todos os arquivos de entrega dos alunos para determinada atividade.
    """
    def get(self, request, *args, **kwargs):
        atividade = get_object_or_404(Atividade, id=self.kwargs.get("atividade_pk"), turma=self.get_turma())
        
        entregas_com_arquivo = atividade.entregas.exclude(arquivo="").select_related("aluno")
        
        if not entregas_com_arquivo.exists():
            messages.warning(request, "Não há arquivos de entrega para baixar nesta atividade.")
            return redirect("turmas:atividade_detalhe", pk=atividade.turma_id, atividade_pk=atividade.pk)

        # Buffer em memória
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for entrega in entregas_com_arquivo:
                if entrega.arquivo and hasattr(entrega.arquivo, 'path'):
                    import os
                    # Nome do arquivo será: [Nome-do-Aluno]-[Nome-Original-do-Arquivo]
                    nome_aluno = slugify(entrega.aluno.nome)
                    nome_original = os.path.basename(entrega.arquivo.name)
                    nome_no_zip = f"{nome_aluno}-{nome_original}"
                    
                    try:
                        zip_file.write(entrega.arquivo.path, arcname=nome_no_zip)
                    except Exception as e:
                        # Em caso de arquivo não encontrado fisicamente
                        print(f"Erro ao zipar {entrega.arquivo.path}: {e}")

        # Configura as respostas HTTP
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type="application/zip")
        nome_zip = f"entregas-{slugify(atividade.titulo)}.zip"
        response["Content-Disposition"] = f'attachment; filename="{nome_zip}"'
        
        return response


class AtividadeListaPublicaView(ListView):
    """View pública para listar todas as atividades publicadas de uma turma."""
    model = Atividade
    template_name = "atividades/lista_publica.html"
    context_object_name = "atividades"

    def get_queryset(self):
        token = self.kwargs.get("token")
        turma = get_object_or_404(Turma, token_publico=token)
        return Atividade.objects.filter(turma=turma, publicada=True).order_by("prazo")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.kwargs.get("token")
        context["turma"] = get_object_or_404(Turma, token_publico=token)
        return context

class AtividadeDetalhePublicoView(DetailView):
    """View pública para ver detalhes de uma atividade (sem poder entregar)."""
    model = Atividade
    template_name = "atividades/detalhe_publico.html"
    context_object_name = "atividade"

    def get_object(self, queryset=None):
        token = self.kwargs.get("token")
        atividade_id = self.kwargs.get("atividade_id")
        turma = get_object_or_404(Turma, token_publico=token)
        return get_object_or_404(Atividade, id=atividade_id, turma=turma, publicada=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.kwargs.get("token")
        context["turma"] = get_object_or_404(Turma, token_publico=token)
        return context

class AvaliarEntregaView(ProfessorRequiredMixin, View):
    """View para avaliar uma entrega via HTMX."""
    
    def get_entrega(self):
        return get_object_or_404(
            Entrega,
            id=self.kwargs.get("entrega_pk"),
            atividade_id=self.kwargs.get("atividade_pk"),
            atividade__turma_id=self.kwargs.get("pk"),
        )

    def get(self, request, *args, **kwargs):
        entrega = self.get_entrega()
        from .forms import AvaliacaoForm
        form = AvaliacaoForm(instance=entrega)
        return render(request, "avaliacoes/_inline_avaliacao.html", {
            "entrega": entrega, 
            "form": form, 
            "edit_mode": True,
            "turma_pk": self.kwargs.get("pk")
        })

    def post(self, request, *args, **kwargs):
        entrega = self.get_entrega()
        from .forms import AvaliacaoForm
        form = AvaliacaoForm(request.POST, instance=entrega)
        if form.is_valid():
            entrega = form.save(commit=False)
            entrega.status = "avaliada"
            entrega.data_avaliacao = timezone.now()
            entrega.save()
            return render(request, "avaliacoes/_inline_avaliacao.html", {
                "entrega": entrega, 
                "form": form, 
                "edit_mode": False,
                "turma_pk": self.kwargs.get("pk")
            })
        return render(request, "avaliacoes/_inline_avaliacao.html", {
            "entrega": entrega, 
            "form": form, 
            "edit_mode": True,
            "turma_pk": self.kwargs.get("pk")
        })


class ReabrirPrazoAlunoView(AtividadeMixin, UpdateView):
    """
    Permite ao professor redefinir o prazo de entrega individualmente
    para um aluno específico, sem alterar o prazo geral da atividade.
    """
    model = Entrega
    form_class = ReabrirPrazoForm
    template_name = "atividades/reabrir_prazo.html"

    def get_object(self, queryset=None):
        atividade = get_object_or_404(
            Atividade,
            id=self.kwargs.get("atividade_pk"),
            turma=self.get_turma(),
        )
        aluno_pk = self.kwargs.get("aluno_pk")
        from alunos.models import Aluno
        aluno = get_object_or_404(Aluno, pk=aluno_pk)

        # Obtém ou cria a Entrega pendente para o aluno poder entregar depois
        entrega, _ = Entrega.objects.get_or_create(
            atividade=atividade,
            aluno=aluno,
            defaults={"status": "pendente"},
        )
        self.atividade = atividade
        self.aluno = aluno
        return entrega

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["atividade"] = self.atividade
        ctx["aluno"] = self.aluno
        return ctx

    def get_success_url(self):
        messages.success(
            self.request,
            f"Prazo de {self.aluno.nome} redefinido para {self.object.prazo_extendido:%d/%m/%Y %H:%M}."
        )
        return reverse(
            "turmas:atividade_detalhe",
            kwargs={"pk": self.kwargs["pk"], "atividade_pk": self.kwargs["atividade_pk"]},
        )
