from django import forms

from .models import Aluno


class AlunoForm(forms.ModelForm):
    """Formulário para criar e editar um aluno."""

    def __init__(self, *args, **kwargs):
        self.allow_existing_email = kwargs.pop("allow_existing_email", False)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.allow_existing_email:
            self._validate_unique = False
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if self.allow_existing_email:
            return email
        return email

    class Meta:
        model = Aluno
        fields = ["nome", "email", "matricula", "avatar", "ativo"]
        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "input-field",
                    "placeholder": "Ex: João da Silva",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "input-field",
                    "placeholder": "Ex: joao@escola.pr.gov.br",
                }
            ),
            "matricula": forms.TextInput(
                attrs={
                    "class": "input-field",
                    "placeholder": "CGM ou RA (opcional)",
                }
            ),
            "avatar": forms.FileInput(
                attrs={
                    "class": "w-full text-sm text-zinc-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-zinc-700 file:text-zinc-200 hover:file:bg-zinc-600",
                }
            ),
            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 rounded border-zinc-600 bg-zinc-800 text-cyan-500 focus:ring-cyan-500",
                }
            ),
        }
