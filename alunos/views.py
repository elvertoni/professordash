import csv
import io
import logging

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from core.mixins import ProfessorRequiredMixin, TurmaPublicaMixin
from turmas.models import Matricula, Turma

from .forms import AlunoForm
from .models import Aluno

logger = logging.getLogger(__name__)


class AlunoMixin:
    """Resolve self.turma a partir do pk da turma na URL."""

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.turma = get_object_or_404(Turma, pk=kwargs["pk"])


class AlunoListView(ProfessorRequiredMixin, AlunoMixin, ListView):
    """Lista os alunos matriculados numa turma com paginação e busca."""

    template_name = "alunos/lista.html"
    context_object_name = "matriculas_page"
    paginate_by = 20

    def get_queryset(self):
        qs = Matricula.objects.filter(turma=self.turma).select_related("aluno")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(aluno__nome__icontains=q) | qs.filter(aluno__email__icontains=q)
        return qs.order_by("aluno__nome")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        ctx["q"] = self.request.GET.get("q", "")
        # Compatibilidade: ctx["matriculas"] aponta para a queryset paginada
        ctx["matriculas"] = ctx["matriculas_page"]
        return ctx


class AlunoCreateView(ProfessorRequiredMixin, AlunoMixin, CreateView):
    """Adiciona um novo aluno e o matricula na turma."""

    model = Aluno
    form_class = AlunoForm
    template_name = "alunos/form.html"

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        
        # Verifica se aluno já existe (por e-mail) para evitar dupla criação
        aluno, created = Aluno.objects.update_or_create(
            email=email,
            defaults={
                "nome": form.cleaned_data.get("nome"),
                "matricula": form.cleaned_data.get("matricula"),
                "ativo": form.cleaned_data.get("ativo"),
                "avatar": form.cleaned_data.get("avatar"),
            }
        )
        
        # Matricula o aluno na turma
        Matricula.objects.get_or_create(aluno=aluno, turma=self.turma)
        
        logger.info(f"Aluno {aluno.nome} ({email}) {'criado e ' if created else ''}matriculado na turma pk={self.turma.pk}")
        messages.success(self.request, f'Aluno "{aluno.nome}" matriculado com sucesso.')
        
        # Atribuimos o aluno ao self.object para o CreateView não quebrar, embora já tenhamos salvo
        self.object = aluno
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("turmas:alunos_lista", kwargs={"pk": self.turma.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        return ctx


class AlunoDetailView(ProfessorRequiredMixin, AlunoMixin, DetailView):
    """Exibe o desempenho do aluno e as submissões dele na turma."""

    template_name = "alunos/detalhe.html"
    context_object_name = "aluno"

    def get_object(self):
        return get_object_or_404(Aluno, pk=self.kwargs["aluno_pk"])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        # Pega as entregas deste aluno relacionadas às atividades desta turma
        ctx["entregas"] = self.object.entregas.filter(atividade__turma=self.turma).select_related("atividade")
        return ctx


class AlunoUpdateView(ProfessorRequiredMixin, AlunoMixin, UpdateView):
    """Edita os dados de um aluno (nome, email, etc)."""

    model = Aluno
    form_class = AlunoForm
    template_name = "alunos/form.html"
    context_object_name = "aluno"

    def get_object(self):
        return get_object_or_404(Aluno, pk=self.kwargs["aluno_pk"])

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Aluno {self.object.nome} atualizado.')
        return response

    def get_success_url(self):
        return reverse_lazy("turmas:alunos_lista", kwargs={"pk": self.turma.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        return ctx


class AlunoRemoverView(ProfessorRequiredMixin, AlunoMixin, View):
    """Desativa a matrícula de um aluno nesta turma via POST."""

    def post(self, request, pk, aluno_pk):
        matricula = get_object_or_404(Matricula, aluno__pk=aluno_pk, turma=self.turma)
        matricula.ativa = False
        matricula.save(update_fields=["ativa"])
        messages.success(request, f'Aluno {matricula.aluno.nome} removido da turma.')
        return redirect("turmas:alunos_lista", pk=self.turma.pk)


class AlunoMoverTurmaView(ProfessorRequiredMixin, AlunoMixin, View):
    """Move um aluno de uma Turma para outra (alterando a Matrícula)."""

    def get(self, request, pk, aluno_pk):
        matricula = get_object_or_404(Matricula, aluno__pk=aluno_pk, turma=self.turma)
        # Turmas ativas do mesmo autor (professor), exceto a atual
        # Assumindo que a Turma tem autorização via ProfessorRequiredMixin no dispatch
        turmas_disponiveis = Turma.objects.filter(ativa=True).exclude(pk=self.turma.pk)
        
        # Filtro de turmas do usuário logado (o professor)
        if hasattr(Turma, "autor"):
            turmas_disponiveis = turmas_disponiveis.filter(autor=request.user)
            
        return render(request, "alunos/mover.html", {
            "turma": self.turma,
            "matricula": matricula,
            "turmas_disponiveis": turmas_disponiveis,
        })

    def post(self, request, pk, aluno_pk):
        matricula = get_object_or_404(Matricula, aluno__pk=aluno_pk, turma=self.turma)
        nova_turma_pk = request.POST.get("nova_turma_pk")
        
        if nova_turma_pk:
            nova_turma = get_object_or_404(Turma, pk=nova_turma_pk)
            # Verifica se já existe matrícula ativa na nova turma para não dar IntegrityError
            if Matricula.objects.filter(aluno=matricula.aluno, turma=nova_turma).exists():
                messages.warning(request, f'O aluno {matricula.aluno.nome} já possui matrícula na turma {nova_turma.nome}. A matrícula atual foi mantida.')
            else:
                matricula.turma = nova_turma
                matricula.save(update_fields=["turma"])
                logger.info(f"Aluno {matricula.aluno.nome} movido da turma {self.turma.pk} para {nova_turma.pk}")
                messages.success(request, f'Aluno {matricula.aluno.nome} transferido para {nova_turma.nome} com sucesso.')
                
        return redirect("turmas:alunos_lista", pk=self.turma.pk)


class AlunoImportarCSVView(ProfessorRequiredMixin, AlunoMixin, View):
    """Importa alunos de um arquivo CSV associando-os à Turma."""

    def get(self, request, pk):
        return render(request, "alunos/importar.html", {"turma": self.turma})

    def post(self, request, pk):
        csv_file = request.FILES.get("arquivo_csv")
        
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, "Por favor, envie um arquivo CSV válido.")
            return redirect("turmas:alunos_importar", pk=self.turma.pk)

        # Lendo arquivo CSV (suporta UTF-8 com BOM, UTF-8 e Latin-1)
        raw = csv_file.read()
        for encoding in ('utf-8-sig', 'utf-8', 'latin-1'):
            try:
                dataset = raw.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            messages.error(request, "Não foi possível decodificar o arquivo CSV. Use UTF-8 ou Latin-1.")
            return redirect("turmas:alunos_importar", pk=self.turma.pk)
        io_string = io.StringIO(dataset)
        reader = csv.DictReader(io_string, delimiter=',')
        
        count = 0
        for row in reader:
            nome = row.get('nome') or row.get('Nome')
            email = row.get('email') or row.get('Email') or row.get('E-mail')
            matricula_num = row.get('matricula') or row.get('Matricula') or row.get('RA')
            
            if nome and email:
                aluno, _ = Aluno.objects.update_or_create(
                    email=email.strip().lower(),
                    defaults={
                        "nome": nome.strip(),
                        "matricula": matricula_num.strip() if matricula_num else "",
                    }
                )
                Matricula.objects.get_or_create(aluno=aluno, turma=self.turma)
                count = count + 1
                
        messages.success(request, f"{count} aluno(s) importado(s) com sucesso para a turma.")
        return redirect("turmas:alunos_lista", pk=self.turma.pk)


class AlunosBuscaHTMXView(ProfessorRequiredMixin, AlunoMixin, View):
    """Fragment HTMX: retorna apenas as linhas da tabela filtradas por nome/email."""

    def get(self, request, pk):
        q = request.GET.get("q", "").strip()
        matriculas = Matricula.objects.filter(turma=self.turma).select_related("aluno")
        if q:
            matriculas = matriculas.filter(
                aluno__nome__icontains=q
            ) | matriculas.filter(
                aluno__email__icontains=q
            )
        matriculas = matriculas.order_by("aluno__nome")

        paginator = Paginator(matriculas, 20)
        page_obj = paginator.get_page(request.GET.get("page", 1))

        return render(request, "alunos/_tabela_alunos.html", {
            "matriculas": page_obj,
            "page_obj": page_obj,
            "turma": self.turma,
            "q": q,
        })


class MinhaAreaView(TurmaPublicaMixin, ListView):
    """Dashboard público do Aluno, acessível via token da turma e exigindo login."""
    
    template_name = "alunos/minha_area.html"
    context_object_name = "atividades_status"

    def get_queryset(self):
        # Como o TurmaPublicaMixin apenas garante que há um token na sessão ou na URL,
        # para acessar a "Minha Área" o usuário deve estar logado e vinculado a um Aluno.
        if not self.request.user.is_authenticated or not hasattr(self.request.user, "aluno"):
            return []
            
        aluno = self.request.user.aluno
        
        # Pega as atividades da turma
        atividades = self.turma.atividades.filter(publicada=True).order_by("prazo")
        
        # Faz um "left join" das entregas do aluno para essas atividades
        entregas_dict = {
            e.atividade_id: e 
            for e in aluno.entregas.filter(atividade__turma=self.turma)
        }
        
        # Constrói o resultado como uma lista de dicionários
        # { "atividade": obj, "entrega": obj_ou_None }
        resultado = []
        for atividade in atividades:
            resultado.append({
                "atividade": atividade,
                "entrega": entregas_dict.get(atividade.pk)
            })
            
        return resultado

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        
        if self.request.user.is_authenticated and hasattr(self.request.user, "aluno"):
            ctx["aluno"] = self.request.user.aluno
            # Verifica se está realmente matriculado
            matricula = aluno_obj = self.request.user.aluno
            ctx["matricula"] = matricula.matriculas.filter(turma=self.turma, ativa=True).first()
            
        return ctx
