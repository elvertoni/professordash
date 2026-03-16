from django import forms
from markdownx.fields import MarkdownxFormField

from .models import Aula


class AulaForm(forms.ModelForm):
    """Formulário para criação e edição de aulas com suporte a Markdown."""

    conteudo = MarkdownxFormField(required=False)

    class Meta:
        model = Aula
        fields = ["titulo", "numero", "data", "conteudo", "ordem"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "input-field"}),
            "numero": forms.NumberInput(attrs={"class": "input-field"}),
            "data": forms.DateInput(
                attrs={"class": "input-field", "type": "date"},
                format="%Y-%m-%d",
            ),
            "ordem": forms.NumberInput(attrs={"class": "input-field"}),
        }
