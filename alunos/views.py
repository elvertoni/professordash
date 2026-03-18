import csv
import io
import logging

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from core.mixins import AlunoAutenticadoMixin, ProfessorRequiredMixin
from turmas.models import Matricula, Turma

from .forms import AlunoForm
from .models import Aluno

logger = logging.getLogger(__name__)


def _reativar_ou_criar_matricula(aluno, turma):
    matricula, created = Matricula.objects.get_or_create(aluno=aluno, turma=turma)
    if not created and not matricula.ativa:
        matricula.ativa = True
        matricula.save(update_fields=["ativa"])
    return matricula, created


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
            qs = qs.filter(aluno__nome__icontains=q) | qs.filter(
                aluno__email__icontains=q
            )
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["allow_existing_email"] = True
        return kwargs

    def form_valid(self, form):
        email = form.cleaned_data["email"].strip().lower()
        aluno = Aluno.objects.filter(email=email).first()
        created = False

        if not aluno:
            aluno = Aluno.objects.create(
                nome=form.cleaned_data["nome"],
                email=email,
                matricula=form.cleaned_data.get("matricula", ""),
                avatar=form.cleaned_data.get("avatar"),
                ativo=form.cleaned_data.get("ativo", True),
            )
            created = True

        matricula, matricula_created = _reativar_ou_criar_matricula(aluno, self.turma)

        logger.info(
            "Aluno %s (%s) %smatriculado na turma pk=%s",
            aluno.nome,
            email,
            "criado e " if created else "",
            self.turma.pk,
        )
        messages.success(self.request, f'Aluno "{aluno.nome}" matriculado com sucesso.')
        if not created and not matricula_created and matricula.ativa:
            messages.info(
                self.request,
                f'O cadastro existente de "{aluno.nome}" foi reaproveitado sem sobrescrever dados globais.',
            )

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
        ctx["entregas"] = self.object.entregas.filter(
            atividade__turma=self.turma
        ).select_related("atividade")
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
        messages.success(self.request, f"Aluno {self.object.nome} atualizado.")
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
        messages.success(request, f"Aluno {matricula.aluno.nome} removido da turma.")
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

        return render(
            request,
            "alunos/mover.html",
            {
                "turma": self.turma,
                "matricula": matricula,
                "turmas_disponiveis": turmas_disponiveis,
            },
        )

    def post(self, request, pk, aluno_pk):
        matricula = get_object_or_404(Matricula, aluno__pk=aluno_pk, turma=self.turma)
        nova_turma_pk = request.POST.get("nova_turma_pk")

        if nova_turma_pk:
            nova_turma = get_object_or_404(Turma, pk=nova_turma_pk)
            # Verifica se já existe matrícula ativa na nova turma para não dar IntegrityError
            if Matricula.objects.filter(
                aluno=matricula.aluno, turma=nova_turma
            ).exists():
                messages.warning(
                    request,
                    f"O aluno {matricula.aluno.nome} já possui matrícula na turma {nova_turma.nome}. A matrícula atual foi mantida.",
                )
            else:
                matricula.turma = nova_turma
                matricula.save(update_fields=["turma"])
                logger.info(
                    f"Aluno {matricula.aluno.nome} movido da turma {self.turma.pk} para {nova_turma.pk}"
                )
                messages.success(
                    request,
                    f"Aluno {matricula.aluno.nome} transferido para {nova_turma.nome} com sucesso.",
                )

        return redirect("turmas:alunos_lista", pk=self.turma.pk)


class AlunoImportarCSVView(ProfessorRequiredMixin, AlunoMixin, View):
    """Importa alunos de um arquivo CSV associando-os à Turma."""

    def get(self, request, pk):
        return render(request, "alunos/importar.html", {"turma": self.turma})

    def post(self, request, pk):
        csv_file = request.FILES.get("arquivo_csv")

        if not csv_file or not csv_file.name.endswith(".csv"):
            messages.error(request, "Por favor, envie um arquivo CSV válido.")
            return redirect("turmas:alunos_importar", pk=self.turma.pk)

        # Lendo arquivo CSV (suporta UTF-8 com BOM, UTF-8 e Latin-1)
        raw = csv_file.read()
        for encoding in ("utf-8-sig", "utf-8", "latin-1"):
            try:
                dataset = raw.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            messages.error(
                request,
                "Não foi possível decodificar o arquivo CSV. Use UTF-8 ou Latin-1.",
            )
            return redirect("turmas:alunos_importar", pk=self.turma.pk)
        io_string = io.StringIO(dataset)
        reader = csv.DictReader(io_string, delimiter=",")

        count = 0
        for row in reader:
            nome = row.get("nome") or row.get("Nome")
            email = row.get("email") or row.get("Email") or row.get("E-mail")
            matricula_num = (
                row.get("matricula") or row.get("Matricula") or row.get("RA")
            )

            if nome and email:
                email_normalizado = email.strip().lower()
                aluno = Aluno.objects.filter(email=email_normalizado).first()
                if not aluno:
                    aluno = Aluno.objects.create(
                        nome=nome.strip(),
                        email=email_normalizado,
                        matricula=matricula_num.strip() if matricula_num else "",
                    )
                _reativar_ou_criar_matricula(aluno, self.turma)
                count = count + 1

        messages.success(
            request, f"{count} aluno(s) importado(s) com sucesso para a turma."
        )
        return redirect("turmas:alunos_lista", pk=self.turma.pk)


class AlunosBuscaHTMXView(ProfessorRequiredMixin, AlunoMixin, View):
    """Fragment HTMX: retorna apenas as linhas da tabela filtradas por nome/email."""

    def get(self, request, pk):
        q = request.GET.get("q", "").strip()
        matriculas = Matricula.objects.filter(turma=self.turma).select_related("aluno")
        if q:
            matriculas = matriculas.filter(
                aluno__nome__icontains=q
            ) | matriculas.filter(aluno__email__icontains=q)
        matriculas = matriculas.order_by("aluno__nome")

        paginator = Paginator(matriculas, 20)
        page_obj = paginator.get_page(request.GET.get("page", 1))

        return render(
            request,
            "alunos/_tabela_alunos.html",
            {
                "matriculas": page_obj,
                "page_obj": page_obj,
                "turma": self.turma,
                "q": q,
            },
        )


class MinhaAreaView(AlunoAutenticadoMixin, ListView):
    """Dashboard público do Aluno, acessível via token da turma e exigindo login."""

    template_name = "alunos/minha_area.html"
    context_object_name = "atividades_status"

    def get_queryset(self):
        aluno = self.matricula.aluno
        atividades = self.turma.atividades.filter(publicada=True).order_by("prazo")

        entregas_dict = {
            e.atividade_id: e
            for e in aluno.entregas.filter(atividade__turma=self.turma)
        }

        resultado = []
        for atividade in atividades:
            resultado.append(
                {"atividade": atividade, "entrega": entregas_dict.get(atividade.pk)}
            )

        return resultado

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        ctx["aluno"] = self.matricula.aluno
        ctx["matricula"] = self.matricula
        return ctx
