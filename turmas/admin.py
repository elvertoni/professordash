from django.contrib import admin

from .models import Matricula, Turma


class MatriculaInline(admin.TabularInline):
    """Inline de matrículas exibido dentro da turma no Django Admin."""

    model = Matricula
    extra = 0
    fields = ("aluno", "ativa", "data_entrada")
    readonly_fields = ("data_entrada",)


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ("nome", "codigo", "periodo", "ano_letivo", "ativa", "criado_em")
    list_filter = ("ativa", "ano_letivo")
    search_fields = ("nome", "codigo")
    readonly_fields = ("token_publico", "criado_em", "atualizado_em")
    inlines = [MatriculaInline]


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ("aluno", "turma", "data_entrada", "ativa")
    list_filter = ("ativa", "turma")
    search_fields = ("aluno__nome", "turma__nome")
    readonly_fields = ("data_entrada", "criado_em", "atualizado_em")
