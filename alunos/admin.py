from django.contrib import admin

from .models import Aluno


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "matricula", "ativo", "criado_em")
    list_filter = ("ativo",)
    search_fields = ("nome", "email", "matricula")
    readonly_fields = ("criado_em", "atualizado_em")
