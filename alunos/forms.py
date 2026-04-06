from django import forms

from .models import Aluno


INPUT_CLASSES = (
    "w-full rounded-2xl border border-outline-variant/15 bg-surface-container-high "
    "px-4 py-3 text-sm text-on-surface placeholder:text-on-surface-variant/40 "
    "outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
)

FILE_INPUT_CLASSES = (
    "block w-full rounded-2xl border border-outline-variant/15 bg-surface-container-high "
    "px-4 py-3 text-sm text-on-surface file:mr-4 file:rounded-full file:border-0 "
    "file:bg-primary file:px-4 file:py-2 file:text-sm file:font-semibold "
    "file:text-on-primary hover:file:bg-primary/90"
)

CHECKBOX_CLASSES = (
    "h-4 w-4 rounded border-outline-variant/20 bg-surface-container-high text-primary "
    "focus:ring-primary/40"
)


class AlunoForm(forms.ModelForm):
    """Formulario para criar e editar um aluno."""

    def __init__(self, *args, **kwargs):
        self.allow_existing_email = kwargs.pop("allow_existing_email", False)
        super().__init__(*args, **kwargs)
        self.existing_email_aluno = None

        self.fields["nome"].label = "Nome completo"
        self.fields["email"].label = "E-mail"
        self.fields["matricula"].label = "Matricula / RA"
        self.fields["matricula"].required = False

        if self.instance.pk:
            self.fields["avatar"].label = "Avatar"
            self.fields["avatar"].required = False
            self.fields["ativo"].label = "Aluno ativo"
            self.fields["ativo"].required = False
        else:
            self.fields.pop("avatar", None)
            self.fields.pop("ativo", None)

    def clean(self):
        cleaned_data = super().clean()
        if self.allow_existing_email:
            self._validate_unique = False
        return cleaned_data

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if not email:
            return email

        existing = Aluno.objects.filter(email=email)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)

        self.existing_email_aluno = existing.first()

        if self.existing_email_aluno and not self.allow_existing_email:
            raise forms.ValidationError(
                "Ja existe um aluno cadastrado com este e-mail."
            )

        return email

    def clean_matricula(self):
        return (self.cleaned_data.get("matricula") or "").strip()

    class Meta:
        model = Aluno
        fields = ["nome", "email", "matricula", "avatar", "ativo"]
        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "Ex: Joao da Silva",
                    "autocomplete": "name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "Ex: joao@escola.edu.br",
                    "autocomplete": "email",
                }
            ),
            "matricula": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "Opcional",
                }
            ),
            "avatar": forms.FileInput(
                attrs={
                    "class": FILE_INPUT_CLASSES,
                    "accept": "image/*",
                }
            ),
            "ativo": forms.CheckboxInput(
                attrs={
                    "class": CHECKBOX_CLASSES,
                }
            ),
        }
