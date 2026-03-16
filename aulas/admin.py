from django.contrib import admin

from .models import Aula


@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ("__str__", "turma", "numero", "data", "realizada", "ordem")
    list_filter = ("realizada", "turma")
    search_fields = ("titulo", "turma__nome")
    readonly_fields = ("criado_em", "atualizado_em")
    ordering = ("turma", "ordem", "numero")
