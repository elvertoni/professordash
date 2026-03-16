from django import forms

from .models import Aluno


class AlunoForm(forms.ModelForm):
    """Formulário para criar e editar um aluno."""

    class Meta:
        model = Aluno
        fields = ["nome", "email", "matricula", "avatar", "ativo"]
        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500",
                    "placeholder": "Ex: João da Silva",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500",
                    "placeholder": "Ex: joao@escola.pr.gov.br",
                }
            ),
            "matricula": forms.TextInput(
                attrs={
                    "class": "w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500",
                    "placeholder": "CGM ou RA (opcional)",
                }
            ),
            "avatar": forms.FileInput(
                attrs={
                    "class": "w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100",
                }
            ),
            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded",
                }
            ),
        }
