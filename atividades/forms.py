from django import forms
from markdownx.fields import MarkdownxFormField

from .models import Atividade


class AtividadeForm(forms.ModelForm):
    descricao = MarkdownxFormField(
        label="Descrição",
        help_text="Aceita formatação em Markdown.",
        widget=forms.Textarea(attrs={"class": "markdownx-editor"}),
    )

    class Meta:
        model = Atividade
        fields = [
            "turma",
            "aula",
            "titulo",
            "descricao",
            "tipo_entrega",
            "prazo",
            "valor_pontos",
            "permitir_reenvio",
            "publicada",
        ]
        widgets = {
            "prazo": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-input"}
            ),
            "turma": forms.Select(attrs={"class": "form-select"}),
            "aula": forms.Select(attrs={"class": "form-select"}),
            "tipo_entrega": forms.Select(attrs={"class": "form-select"}),
            "titulo": forms.TextInput(attrs={"class": "form-input"}),
            "valor_pontos": forms.NumberInput(attrs={"class": "form-input", "step": "0.1"}),
            "permitir_reenvio": forms.CheckboxInput(
                attrs={"class": "rounded border-slate-300 text-brand-600 focus:ring-brand-600"}
            ),
            "publicada": forms.CheckboxInput(
                attrs={"class": "rounded border-slate-300 text-brand-600 focus:ring-brand-600"}
            ),
        }

    def __init__(self, *args, **kwargs):
        turma_id = kwargs.pop("turma_id", None)
        super().__init__(*args, **kwargs)
        if turma_id:
            from turmas.models import Turma
            from aulas.models import Aula
            
            # Limita as turmas à turma atual, se informada
            self.fields["turma"].queryset = Turma.objects.filter(id=turma_id)
            self.fields["turma"].initial = turma_id
            
            # Limita as aulas à turma atual, se informada
            self.fields["aula"].queryset = Aula.objects.filter(turma_id=turma_id)

from core.validators import validar_arquivo
from .models import Entrega, TipoEntrega, Atividade

class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ["arquivo", "texto", "url"]
        widgets = {
            "texto": forms.Textarea(attrs={"class": "form-input", "rows": 5, "x-show": "tipo_entrega === 'texto'"}),
            "url": forms.URLInput(attrs={"class": "form-input", "x-show": "tipo_entrega === 'link'"}),
            "arquivo": forms.FileInput(attrs={"class": "form-input", "x-show": "tipo_entrega === 'arquivo'"}),
        }

    def __init__(self, *args, **kwargs):
        self.atividade = kwargs.pop("atividade", None)
        super().__init__(*args, **kwargs)
        
        # Oculta campos que não são do tipo da atividade atual
        if self.atividade:
            if self.atividade.tipo_entrega == TipoEntrega.ARQUIVO:
                self.fields["texto"].widget = forms.HiddenInput()
                self.fields["url"].widget = forms.HiddenInput()
                self.fields["arquivo"].required = True
            elif self.atividade.tipo_entrega == TipoEntrega.TEXTO:
                self.fields["arquivo"].widget = forms.HiddenInput()
                self.fields["url"].widget = forms.HiddenInput()
                self.fields["texto"].required = True
            elif self.atividade.tipo_entrega == TipoEntrega.LINK:
                self.fields["arquivo"].widget = forms.HiddenInput()
                self.fields["texto"].widget = forms.HiddenInput()
                self.fields["url"].required = True

    def clean_arquivo(self):
        arquivo = self.cleaned_data.get("arquivo")
        if arquivo and getattr(self, "atividade", None) and self.atividade.tipo_entrega == TipoEntrega.ARQUIVO:
            # Usando o core.validators.validar_arquivo
            validar_arquivo(arquivo)
        return arquivo

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ["nota", "feedback"]
        widgets = {
            "nota": forms.NumberInput(attrs={
                "class": "form-input px-2 py-1 h-8 text-sm w-20", 
                "step": "0.1", "min": "0", "max": "100", 
                "placeholder": "Nota"
            }),
            "feedback": forms.Textarea(attrs={
                "class": "form-input px-2 py-1 text-sm w-full", 
                "rows": 2, 
                "placeholder": "Feedback (opcional)"
            }),
        }


class ReabrirPrazoForm(forms.ModelForm):
    """Permite ao professor definir um prazo individual para um aluno."""

    class Meta:
        model = Entrega
        fields = ["prazo_extendido"]
        widgets = {
            "prazo_extendido": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-input"},
                format="%Y-%m-%dT%H:%M",
            ),
        }
        labels = {
            "prazo_extendido": "Novo prazo para este aluno",
        }
