from datetime import date

from django import forms

from .models import Turma

PERIODOS = [
    ("", "Selecione..."),
    ("1º Semestre", "1º Semestre"),
    ("2º Semestre", "2º Semestre"),
    ("1º Trimestre", "1º Trimestre"),
    ("2º Trimestre", "2º Trimestre"),
    ("3º Trimestre", "3º Trimestre"),
    ("Anual", "Anual"),
]


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
            "ano_letivo": forms.NumberInput(
                attrs={"class": "input-field"}
            ),
            "descricao": forms.Textarea(
                attrs={"class": "input-field", "rows": 3}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pré-preencher o ano letivo com o ano atual apenas na criação
        if not self.instance.pk:
            self.fields["ano_letivo"].initial = date.today().year
        # Converter o campo período em select com opções predefinidas
        self.fields["periodo"].widget = forms.Select(
            choices=PERIODOS,
            attrs={"class": "input-field"},
        )
