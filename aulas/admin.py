from django.contrib import admin

from .models import Aula


@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "turma",
        "numero",
        "data",
        "realizada",
        "gera_apostila",
        "ordem",
    )
    list_filter = ("realizada", "gera_apostila", "turma")
    search_fields = ("titulo", "turma__nome")
    readonly_fields = ("criado_em", "atualizado_em")
    ordering = ("turma", "ordem", "numero")
