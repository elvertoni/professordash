from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import Turma

INPUT_CLASSES = (
    "w-full rounded-2xl border border-outline-variant/15 bg-surface-container-high "
    "px-4 py-3 text-sm text-on-surface placeholder:text-on-surface-variant/40 "
    "outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
)

TEXTAREA_CLASSES = (
    "w-full rounded-2xl border border-outline-variant/15 bg-surface-container-high "
    "px-4 py-3 text-sm text-on-surface placeholder:text-on-surface-variant/40 "
    "outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
)

PERIODO_CHOICES = [
    ("1 Trimestre", "1º Trimestre"),
    ("2 Trimestre", "2º Trimestre"),
    ("3 Trimestre", "3º Trimestre"),
    ("1 Semestre", "1º Semestre"),
    ("2 Semestre", "2º Semestre"),
]


def gerar_codigo_turma(nome, ano_letivo, max_length=20):
    base_nome = slugify(nome or "")
    ano = str(ano_letivo or "").strip()

    if not base_nome and not ano:
        return ""
    if not base_nome:
        return ano[:max_length]
    if not ano:
        return base_nome[:max_length]

    suffix = f"-{ano}"
    prefix_limit = max_length - len(suffix)
    if prefix_limit <= 0:
        return ano[:max_length]

    return f"{base_nome[:prefix_limit]}{suffix}"


class TurmaForm(forms.ModelForm):
    """Formulario para criacao e edicao de turmas."""

    periodo = forms.ChoiceField(
        choices=PERIODO_CHOICES,
        widget=forms.Select(attrs={"class": INPUT_CLASSES}),
        label="Periodo letivo",
    )

    class Meta:
        model = Turma
        fields = ["nome", "codigo", "periodo", "ano_letivo", "descricao"]
        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "Ex: Desenvolvimento de Sistemas",
                    "autocomplete": "off",
                }
            ),
            "codigo": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "Gerado automaticamente",
                    "autocomplete": "off",
                }
            ),
            "ano_letivo": forms.NumberInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "min": 2000,
                    "max": 2100,
                }
            ),
            "descricao": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASSES,
                    "rows": 4,
                    "placeholder": "Resumo opcional para identificar a turma.",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["codigo"].required = False
        self.fields["codigo"].help_text = (
            "Gerado a partir do nome e do ano letivo, mas voce pode ajustar."
        )
        self.fields["descricao"].required = False
        if not self.instance.pk:
            self.fields["ano_letivo"].initial = date.today().year

    def clean_codigo(self):
        codigo = (self.cleaned_data.get("codigo") or "").strip()
        if not codigo:
            return ""

        normalized = slugify(codigo)
        if not normalized:
            raise ValidationError("Informe um codigo valido para a turma.")
        if len(normalized) > Turma._meta.get_field("codigo").max_length:
            raise ValidationError("Use no maximo 20 caracteres no codigo.")
        return normalized

    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get("nome")
        ano_letivo = cleaned_data.get("ano_letivo")
        codigo = cleaned_data.get("codigo")

        if not codigo:
            codigo = gerar_codigo_turma(nome, ano_letivo)
            if not codigo:
                self.add_error(
                    "codigo",
                    "Nao foi possivel gerar o codigo automaticamente. Revise nome e ano letivo.",
                )
            else:
                cleaned_data["codigo"] = codigo

        return cleaned_data
