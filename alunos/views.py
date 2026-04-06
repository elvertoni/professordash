import csv
import io
import logging

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
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
    reactivated = False
    if not created and not matricula.ativa:
        matricula.ativa = True
        matricula.save(update_fields=["ativa"])
        reactivated = True
    return matricula, created, reactivated


def _decode_uploaded_csv_file(csv_file):
    raw = csv_file.read()
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def _get_csv_reader(csv_file):
    dataset = _decode_uploaded_csv_file(csv_file)
    if dataset is None:
        return None
    return csv.DictReader(io.StringIO(dataset), delimiter=",")


def _row_value(row, *aliases):
    normalized_row = {
        (key or "").strip().lower(): (value or "").strip() for key, value in row.items()
    }
    for alias in aliases:
        value = normalized_row.get(alias.strip().lower(), "")
        if value:
            return value
    return ""


def _build_csv_report():
    return {
        "total_linhas": 0,
        "sucesso": 0,
        "alunos_criados": 0,
        "alunos_reutilizados": 0,
        "matriculas_criadas": 0,
        "matriculas_reativadas": 0,
        "ja_matriculados": 0,
        "linhas_com_erro": 0,
        "linhas": [],
    }


def _processar_importacao_turma(reader, turma):
    report = _build_csv_report()

    for line_number, row in enumerate(reader, start=2):
        report["total_linhas"] += 1
        nome = _row_value(row, "nome")
        email = _row_value(row, "email", "e-mail")
        matricula_num = _row_value(row, "matricula", "ra")

        if not nome or not email:
            report["linhas_com_erro"] += 1
            report["linhas"].append(
                {
                    "linha": line_number,
                    "status": "erro",
                    "mensagem": "Campos obrigatorios ausentes. Use nome e email.",
                    "nome": nome,
                    "email": email,
                    "matricula": matricula_num,
                }
            )
            continue

        email_normalizado = email.lower()
        aluno = Aluno.objects.filter(email=email_normalizado).first()
        aluno_criado = False

        if not aluno:
            aluno = Aluno.objects.create(
                nome=nome,
                email=email_normalizado,
                matricula=matricula_num,
            )
            aluno_criado = True
            report["alunos_criados"] += 1
        else:
            report["alunos_reutilizados"] += 1

        _, matricula_criada, matricula_reativada = _reativar_ou_criar_matricula(
            aluno,
            turma,
        )

        if matricula_criada:
            report["matriculas_criadas"] += 1
        elif matricula_reativada:
            report["matriculas_reativadas"] += 1
        else:
            report["ja_matriculados"] += 1

        report["sucesso"] += 1
        report["linhas"].append(
            {
                "linha": line_number,
                "status": "sucesso",
                "mensagem": (
                    "Aluno criado e matriculado."
                    if aluno_criado and matricula_criada
                    else "Cadastro existente reutilizado e matricula criada."
                    if matricula_criada
                    else "Cadastro existente reutilizado e matricula reativada."
                    if matricula_reativada
                    else "Aluno ja cadastrado e matricula ja ativa."
                ),
                "nome": aluno.nome,
                "email": aluno.email,
                "matricula": aluno.matricula,
            }
        )

    return report


def _build_csv_preview(reader, turma, preview_limit=6):
    preview = {
        "headers": [header.strip() for header in (reader.fieldnames or []) if header],
        "rows": [],
        "total_linhas_lidas": 0,
        "has_more_rows": False,
        "criar": 0,
        "reutilizar": 0,
        "ja_matriculado": 0,
        "erros": 0,
    }

    for index, row in enumerate(reader, start=2):
        preview["total_linhas_lidas"] += 1
        nome = _row_value(row, "nome")
        email = _row_value(row, "email", "e-mail")
        matricula_num = _row_value(row, "matricula", "ra")

        if not nome or not email:
            status = "erro"
            acao = "Corrigir linha"
            detalhe = "Nome e e-mail sao obrigatorios."
            preview["erros"] += 1
        else:
            aluno = Aluno.objects.filter(email=email.lower()).first()
            matricula_existente = False
            if aluno:
                matricula_existente = Matricula.objects.filter(
                    aluno=aluno,
                    turma=turma,
                    ativa=True,
                ).exists()

            if not aluno:
                status = "novo"
                acao = "Criar aluno e matricular"
                detalhe = "Cadastro novo."
                preview["criar"] += 1
            elif matricula_existente:
                status = "matriculado"
                acao = "Manter matricula ativa"
                detalhe = "Aluno ja esta nesta turma."
                preview["ja_matriculado"] += 1
            else:
                status = "existente"
                acao = "Reutilizar cadastro"
                detalhe = "Aluno existente sera matriculado nesta turma."
                preview["reutilizar"] += 1

        if len(preview["rows"]) < preview_limit:
            preview["rows"].append(
                {
                    "linha": index,
                    "nome": nome,
                    "email": email,
                    "matricula": matricula_num,
                    "status": status,
                    "acao": acao,
                    "detalhe": detalhe,
                }
            )
        else:
            preview["has_more_rows"] = True

    return preview


class AlunoMixin:
    """Resolve self.turma a partir do pk da turma na URL."""

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.turma = get_object_or_404(Turma, pk=kwargs["pk"])


class AlunoListView(ProfessorRequiredMixin, AlunoMixin, ListView):
    """Lista os alunos matriculados numa turma com paginacao e busca."""

    template_name = "alunos/lista.html"
    context_object_name = "matriculas_page"
    paginate_by = 20

    def get_queryset(self):
        qs = Matricula.objects.filter(turma=self.turma).select_related("aluno", "turma")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(aluno__nome__icontains=q) | Q(aluno__email__icontains=q))
        return qs.order_by("aluno__nome")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        ctx["q"] = self.request.GET.get("q", "")
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

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["email"].widget.attrs.update(
            {
                "hx-get": reverse_lazy(
                    "turmas:alunos_email_feedback",
                    kwargs={"pk": self.turma.pk},
                ),
                "hx-trigger": "blur changed delay:300ms",
                "hx-target": "#email-feedback",
                "hx-swap": "innerHTML",
            }
        )
        return form

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        aluno = form.existing_email_aluno or Aluno.objects.filter(email=email).first()
        created = False

        if not aluno:
            aluno = Aluno.objects.create(
                nome=form.cleaned_data["nome"],
                email=email,
                matricula=form.cleaned_data.get("matricula", ""),
            )
            created = True

        _, matricula_created, matricula_reativada = _reativar_ou_criar_matricula(
            aluno,
            self.turma,
        )

        logger.info(
            "Aluno %s (%s) %smatriculado na turma pk=%s",
            aluno.nome,
            email,
            "criado e " if created else "",
            self.turma.pk,
        )

        if created:
            messages.success(
                self.request,
                f'Aluno "{aluno.nome}" criado e matriculado com sucesso.',
            )
        elif matricula_created:
            messages.success(
                self.request,
                f'Aluno "{aluno.nome}" ja existia e foi matriculado nesta turma.',
            )
        elif matricula_reativada:
            messages.success(
                self.request,
                f'A matricula de "{aluno.nome}" foi reativada nesta turma.',
            )
        else:
            messages.info(
                self.request,
                f'O cadastro de "{aluno.nome}" ja existia e a matricula desta turma ja estava ativa.',
            )

        self.object = aluno
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("turmas:alunos_lista", kwargs={"pk": self.turma.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        ctx["is_create"] = True
        ctx["show_avatar_field"] = "avatar" in ctx["form"].fields
        ctx["show_ativo_field"] = "ativo" in ctx["form"].fields
        return ctx


class AlunoDetailView(ProfessorRequiredMixin, AlunoMixin, DetailView):
    """Exibe o desempenho do aluno e as submissões dele na turma."""

    template_name = "alunos/detalhe.html"
    context_object_name = "aluno"

    def get_object(self):
        return get_object_or_404(
            Aluno,
            pk=self.kwargs["aluno_pk"],
            matriculas__turma=self.turma,
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        ctx["entregas"] = self.object.entregas.filter(
            atividade__turma=self.turma
        ).select_related("atividade")
        return ctx


class AlunoUpdateView(ProfessorRequiredMixin, AlunoMixin, UpdateView):
    """Edita os dados de um aluno."""

    model = Aluno
    form_class = AlunoForm
    template_name = "alunos/form.html"
    context_object_name = "aluno"

    def get_object(self):
        return get_object_or_404(
            Aluno,
            pk=self.kwargs["aluno_pk"],
            matriculas__turma=self.turma,
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Aluno {self.object.nome} atualizado.")
        return response

    def get_success_url(self):
        return reverse_lazy("turmas:alunos_lista", kwargs={"pk": self.turma.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["turma"] = self.turma
        ctx["is_create"] = False
        ctx["show_avatar_field"] = "avatar" in ctx["form"].fields
        ctx["show_ativo_field"] = "ativo" in ctx["form"].fields
        return ctx


class AlunoRemoverView(ProfessorRequiredMixin, AlunoMixin, View):
    """Desativa a matricula de um aluno nesta turma via POST."""

    def post(self, request, pk, aluno_pk):
        matricula = get_object_or_404(
            Matricula.objects.select_related("aluno"),
            aluno__pk=aluno_pk,
            turma=self.turma,
        )
        matricula.ativa = False
        matricula.save(update_fields=["ativa"])
        messages.success(request, f"Aluno {matricula.aluno.nome} removido da turma.")
        return redirect("turmas:alunos_lista", pk=self.turma.pk)


class AlunoMoverTurmaView(ProfessorRequiredMixin, AlunoMixin, View):
    """Move um aluno de uma turma para outra."""

    def get(self, request, pk, aluno_pk):
        matricula = get_object_or_404(
            Matricula.objects.select_related("aluno"),
            aluno__pk=aluno_pk,
            turma=self.turma,
        )
        turmas_disponiveis = Turma.objects.filter(ativa=True).exclude(pk=self.turma.pk)

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
        matricula = get_object_or_404(
            Matricula.objects.select_related("aluno"),
            aluno__pk=aluno_pk,
            turma=self.turma,
        )
        nova_turma_pk = request.POST.get("nova_turma_pk")

        if nova_turma_pk:
            turmas_disponiveis = Turma.objects.filter(ativa=True).exclude(pk=self.turma.pk)
            if hasattr(Turma, "autor"):
                turmas_disponiveis = turmas_disponiveis.filter(autor=request.user)
            nova_turma = get_object_or_404(turmas_disponiveis, pk=nova_turma_pk)
            if Matricula.objects.filter(aluno=matricula.aluno, turma=nova_turma).exists():
                messages.warning(
                    request,
                    f"O aluno {matricula.aluno.nome} ja possui matricula na turma {nova_turma.nome}. A matricula atual foi mantida.",
                )
            else:
                matricula.turma = nova_turma
                matricula.save(update_fields=["turma"])
                logger.info(
                    "Aluno %s movido da turma %s para %s",
                    matricula.aluno.nome,
                    self.turma.pk,
                    nova_turma.pk,
                )
                messages.success(
                    request,
                    f"Aluno {matricula.aluno.nome} transferido para {nova_turma.nome} com sucesso.",
                )

        return redirect("turmas:alunos_lista", pk=self.turma.pk)


class AlunoImportarCSVView(ProfessorRequiredMixin, AlunoMixin, View):
    """Importa alunos de um arquivo CSV associando-os a turma."""

    def get(self, request, pk):
        return render(
            request,
            "alunos/importar.html",
            {"turma": self.turma, "report": None},
        )

    def post(self, request, pk):
        csv_file = request.FILES.get("arquivo_csv")
        context = {"turma": self.turma, "report": None}

        if not csv_file or not csv_file.name.endswith(".csv"):
            messages.error(request, "Por favor, envie um arquivo CSV valido.")
            return render(request, "alunos/importar.html", context, status=400)

        reader = _get_csv_reader(csv_file)
        if reader is None:
            messages.error(
                request,
                "Nao foi possivel decodificar o arquivo CSV. Use UTF-8 ou Latin-1.",
            )
            return render(request, "alunos/importar.html", context, status=400)

        report = _processar_importacao_turma(reader, self.turma)
        context["report"] = report

        if report["sucesso"]:
            messages.success(
                request,
                (
                    f"Importacao concluida: {report['alunos_criados']} criado(s), "
                    f"{report['alunos_reutilizados']} reutilizado(s) e "
                    f"{report['linhas_com_erro']} linha(s) com erro."
                ),
            )
        if report["linhas_com_erro"]:
            messages.warning(
                request,
                f"{report['linhas_com_erro']} linha(s) precisam de ajuste antes de uma nova importacao.",
            )

        return render(request, "alunos/importar.html", context)


class AlunoImportarCSVPreviewView(ProfessorRequiredMixin, AlunoMixin, View):
    """Retorna uma pre-visualizacao HTMX das primeiras linhas do CSV."""

    def post(self, request, pk):
        csv_file = request.FILES.get("arquivo_csv")

        if not csv_file or not csv_file.name.endswith(".csv"):
            return render(
                request,
                "alunos/_csv_preview.html",
                {
                    "turma": self.turma,
                    "preview_error": "Selecione um arquivo CSV valido para gerar a pre-visualizacao.",
                },
                status=400,
            )

        reader = _get_csv_reader(csv_file)
        if reader is None:
            return render(
                request,
                "alunos/_csv_preview.html",
                {
                    "turma": self.turma,
                    "preview_error": "Nao foi possivel ler o arquivo. Use UTF-8 ou Latin-1.",
                },
                status=400,
            )

        preview = _build_csv_preview(reader, self.turma)
        return render(
            request,
            "alunos/_csv_preview.html",
            {"turma": self.turma, "preview": preview},
        )


class AlunoImportarMultiturmaCSVView(ProfessorRequiredMixin, View):
    """Importa alunos e matriculas para varias turmas a partir de um CSV."""

    template_name = "alunos/importar_multiturma.html"

    def get(self, request):
        return render(request, self.template_name, {"report": None})

    def post(self, request):
        csv_file = request.FILES.get("arquivo_csv")
        context = {"report": None}

        if not csv_file or not csv_file.name.endswith(".csv"):
            messages.error(request, "Por favor, envie um arquivo CSV valido.")
            return render(request, self.template_name, context, status=400)

        reader = _get_csv_reader(csv_file)
        if reader is None:
            messages.error(
                request,
                "Nao foi possivel decodificar o arquivo CSV. Use UTF-8 ou Latin-1.",
            )
            return render(request, self.template_name, context, status=400)

        report = _build_csv_report()

        for line_number, row in enumerate(reader, start=2):
            report["total_linhas"] += 1
            nome = _row_value(row, "nome")
            email = _row_value(row, "email", "e-mail")
            matricula_num = _row_value(row, "matricula", "ra")
            turma_nome = _row_value(row, "turma")

            if not nome or not email or not turma_nome:
                report["linhas_com_erro"] += 1
                report["linhas"].append(
                    {
                        "linha": line_number,
                        "status": "erro",
                        "mensagem": "Campos obrigatorios ausentes. Use nome, email e turma.",
                        "nome": nome,
                        "email": email,
                        "matricula": matricula_num,
                        "turma": turma_nome,
                    }
                )
                continue

            turmas = list(Turma.objects.filter(nome__iexact=turma_nome).order_by("pk"))
            if not turmas:
                report["linhas_com_erro"] += 1
                report["linhas"].append(
                    {
                        "linha": line_number,
                        "status": "erro",
                        "mensagem": f'Turma "{turma_nome}" nao encontrada.',
                        "nome": nome,
                        "email": email,
                        "matricula": matricula_num,
                        "turma": turma_nome,
                    }
                )
                continue

            if len(turmas) > 1:
                report["linhas_com_erro"] += 1
                report["linhas"].append(
                    {
                        "linha": line_number,
                        "status": "erro",
                        "mensagem": f'Turma "{turma_nome}" e ambigua. Ajuste o nome no CSV.',
                        "nome": nome,
                        "email": email,
                        "matricula": matricula_num,
                        "turma": turma_nome,
                    }
                )
                continue

            turma = turmas[0]
            email_normalizado = email.lower()
            aluno = Aluno.objects.filter(email=email_normalizado).first()
            aluno_criado = False

            if not aluno:
                aluno = Aluno.objects.create(
                    nome=nome,
                    email=email_normalizado,
                    matricula=matricula_num,
                )
                aluno_criado = True
                report["alunos_criados"] += 1
            else:
                report["alunos_reutilizados"] += 1

            _, matricula_criada, matricula_reativada = _reativar_ou_criar_matricula(
                aluno,
                turma,
            )

            if matricula_criada:
                report["matriculas_criadas"] += 1
            elif matricula_reativada:
                report["matriculas_reativadas"] += 1
            else:
                report["ja_matriculados"] += 1

            report["sucesso"] += 1
            report["linhas"].append(
                {
                    "linha": line_number,
                    "status": "sucesso",
                    "mensagem": (
                        "Aluno criado e matricula criada."
                        if aluno_criado and matricula_criada
                        else "Aluno existente reutilizado e matricula criada."
                        if matricula_criada
                        else "Matricula reativada."
                        if matricula_reativada
                        else "Aluno e matricula ja existentes."
                    ),
                    "nome": aluno.nome,
                    "email": aluno.email,
                    "matricula": aluno.matricula,
                    "turma": turma.nome,
                }
            )

        if report["sucesso"]:
            messages.success(
                request,
                f"Importacao concluida: {report['sucesso']} linha(s) processada(s) com sucesso.",
            )
        if report["linhas_com_erro"]:
            messages.warning(
                request,
                f"{report['linhas_com_erro']} linha(s) nao puderam ser importadas.",
            )

        context["report"] = report
        return render(request, self.template_name, context)


class AlunosBuscaHTMXView(ProfessorRequiredMixin, AlunoMixin, View):
    """Fragment HTMX: retorna apenas as linhas da tabela filtradas por nome/email."""

    def get(self, request, pk):
        q = request.GET.get("q", "").strip()
        matriculas = Matricula.objects.filter(turma=self.turma).select_related(
            "aluno",
            "turma",
        )
        if q:
            matriculas = matriculas.filter(
                Q(aluno__nome__icontains=q) | Q(aluno__email__icontains=q)
            )
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


class AlunoEmailFeedbackView(ProfessorRequiredMixin, AlunoMixin, View):
    """Retorna feedback visual sobre e-mail ja existente."""

    def get(self, request, pk):
        email = (request.GET.get("email") or "").strip().lower()
        existing_aluno = Aluno.objects.filter(email=email).first() if email else None
        return render(
            request,
            "alunos/_email_feedback.html",
            {
                "email": email,
                "existing_aluno": existing_aluno,
            },
        )


class MinhaAreaView(AlunoAutenticadoMixin, ListView):
    """Dashboard publico do aluno, acessivel via token da turma e exigindo login."""

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
