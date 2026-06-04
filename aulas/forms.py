from django import forms
from markdownx.fields import MarkdownxFormField

from .models import Aula


class AulaForm(forms.ModelForm):
    """Formulário para criação e edição de aulas com suporte a Markdown."""

    conteudo = MarkdownxFormField(required=False)

    class Meta:
        model = Aula
        fields = [
            "titulo",
            "numero",
            "data",
            "imagem_capa",
            "status",
            "gera_apostila",
            "conteudo",
            "ordem",
        ]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "input-field"}),
            "numero": forms.NumberInput(attrs={"class": "input-field"}),
            "data": forms.DateInput(
                attrs={"class": "input-field", "type": "date"},
                format="%Y-%m-%d",
            ),
            "ordem": forms.NumberInput(attrs={"class": "input-field"}),
            "gera_apostila": forms.CheckboxInput(
                attrs={
                    "class": (
                        "h-4 w-4 rounded border-outline-variant/20 "
                        "bg-surface-container text-primary focus:ring-primary/30"
                    )
                }
            ),
        }
