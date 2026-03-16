from django import forms

from core.validators import TIPOS_PERMITIDOS_MATERIAL, validar_arquivo

from .models import Material, TipoMaterial


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = [
            "turma",
            "aula",
            "titulo",
            "descricao",
            "tipo",
            "visibilidade",
            "arquivo",
            "url_externa",
            "conteudo_md",
            "ordem",
        ]

    def __init__(self, *args, **kwargs):
        self.turma = kwargs.pop("turma", None)
        super().__init__(*args, **kwargs)

        if self.turma:
            self.fields["aula"].queryset = self.turma.aulas.all()
            self.fields["turma"].initial = self.turma
            self.fields["turma"].widget = forms.HiddenInput()

        # Estilos base pros campos
        for field_name, field in self.fields.items():
            if field_name != "turma":
                # Adiciona base styles para form controls (se não for checkbox/radio)
                if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                    field.widget.attrs.update(
                        {
                            "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        }
                    )

    def clean_arquivo(self):
        arquivo = self.cleaned_data.get("arquivo")
        if arquivo:
            validar_arquivo(arquivo, TIPOS_PERMITIDOS_MATERIAL)
        return arquivo

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo")
        arquivo = cleaned_data.get("arquivo")
        url_externa = cleaned_data.get("url_externa")
        conteudo_md = cleaned_data.get("conteudo_md")

        # Limpa erros anteriores do model, e trata a logica condicional individualmente
        if tipo in [TipoMaterial.PDF, TipoMaterial.ZIP, TipoMaterial.ARQUIVO]:
            if not arquivo:
                self.add_error("arquivo", "Este tipo de material exige o envio de um arquivo.")
            # Limpa the fields that should not exist
            cleaned_data["url_externa"] = ""
            cleaned_data["conteudo_md"] = ""

        elif tipo == TipoMaterial.LINK:
            if not url_externa:
                self.add_error("url_externa", "Este tipo de material exige uma URL.")
            cleaned_data["arquivo"] = None
            cleaned_data["conteudo_md"] = ""

        elif tipo == TipoMaterial.MARKDOWN:
            if not conteudo_md:
                self.add_error("conteudo_md", "Este tipo de material exige conteúdo preenchido.")
            cleaned_data["arquivo"] = None
            cleaned_data["url_externa"] = ""

        return cleaned_data
