from django import forms
from markdownx.fields import MarkdownxFormField

from core.validators import TIPOS_PERMITIDOS_ENTREGA, validar_arquivo

from .models import Atividade, Entrega, TipoEntrega


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
                attrs={"type": "datetime-local", "class": "input-field"}
            ),
            "turma": forms.Select(attrs={"class": "input-field"}),
            "aula": forms.Select(attrs={"class": "input-field"}),
            "tipo_entrega": forms.Select(attrs={"class": "input-field"}),
            "titulo": forms.TextInput(attrs={"class": "input-field"}),
            "valor_pontos": forms.NumberInput(
                attrs={"class": "input-field", "step": "0.1"}
            ),
            "permitir_reenvio": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 rounded border-zinc-600 bg-zinc-800 text-cyan-500 focus:ring-cyan-500"
                }
            ),
            "publicada": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 rounded border-zinc-600 bg-zinc-800 text-cyan-500 focus:ring-cyan-500"
                }
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


class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ["arquivo", "texto", "url"]
        widgets = {
            "texto": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "rows": 5,
                    "x-show": "tipo_entrega === 'texto'",
                }
            ),
            "url": forms.URLInput(
                attrs={"class": "form-input", "x-show": "tipo_entrega === 'link'"}
            ),
            "arquivo": forms.FileInput(
                attrs={"class": "form-input", "x-show": "tipo_entrega === 'arquivo'"}
            ),
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
        if (
            arquivo
            and getattr(self, "atividade", None)
            and self.atividade.tipo_entrega == TipoEntrega.ARQUIVO
        ):
            validar_arquivo(arquivo, TIPOS_PERMITIDOS_ENTREGA)
        return arquivo


class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ["nota", "feedback"]
        widgets = {
            "nota": forms.NumberInput(
                attrs={
                    "class": "input-field px-2 py-1 h-8 text-sm w-20",
                    "step": "0.1",
                    "min": "0",
                    "max": "100",
                    "placeholder": "Nota",
                }
            ),
            "feedback": forms.Textarea(
                attrs={
                    "class": "input-field px-2 py-1 text-sm w-full",
                    "rows": 2,
                    "placeholder": "Feedback (opcional)",
                }
            ),
        }

    def clean_nota(self):
        nota = self.cleaned_data.get("nota")
        if nota is None:
            return nota

        if nota < 0:
            raise forms.ValidationError("A nota não pode ser negativa.")

        atividade = getattr(self.instance, "atividade", None)
        if atividade and nota > atividade.valor_pontos:
            raise forms.ValidationError(
                f"A nota não pode ser maior que o valor da atividade ({atividade.valor_pontos})."
            )
        return nota


class ReabrirPrazoForm(forms.ModelForm):
    """Permite ao professor definir um prazo individual para um aluno."""

    class Meta:
        model = Entrega
        fields = ["prazo_extendido"]
        widgets = {
            "prazo_extendido": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "input-field"},
                format="%Y-%m-%dT%H:%M",
            ),
        }
        labels = {
            "prazo_extendido": "Novo prazo para este aluno",
        }
