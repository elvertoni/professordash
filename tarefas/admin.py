from django.contrib import admin

from .models import RealizacaoTarefa, Tarefa


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ("nome", "turma", "data", "ordem", "criado_em")
    list_filter = ("turma", "data")
    search_fields = ("nome", "turma__nome")
    readonly_fields = ("criado_em", "atualizado_em")
    ordering = ("turma", "ordem", "criado_em")


@admin.register(RealizacaoTarefa)
class RealizacaoTarefaAdmin(admin.ModelAdmin):
    list_display = ("tarefa", "aluno", "realizada", "criado_em")
    list_filter = ("realizada", "tarefa__turma")
    search_fields = ("tarefa__nome", "aluno__nome", "aluno__email")
    readonly_fields = ("criado_em", "atualizado_em")
    ordering = ("tarefa", "aluno")
