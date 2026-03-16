from django import forms

from .models import Turma


class TurmaForm(forms.ModelForm):
    """Formulário para criação e edição de turmas."""

    class Meta:
        model = Turma
        fields = ["nome", "codigo", "periodo", "ano_letivo", "descricao"]
        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "input-field",
                    "placeholder": "Ex: Desenvolvimento de Sistemas 1A",
                }
            ),
            "codigo": forms.TextInput(
                attrs={
                    "class": "input-field",
                    "placeholder": "Ex: DS1A-2026",
                }
            ),
            "periodo": forms.TextInput(
                attrs={
                    "class": "input-field",
                    "placeholder": "Ex: 1º Semestre",
                }
            ),
            "ano_letivo": forms.NumberInput(
                attrs={"class": "input-field"}
            ),
            "descricao": forms.Textarea(
                attrs={"class": "input-field", "rows": 3}
            ),
        }
