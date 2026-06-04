from django.contrib import admin

from .models import Aula


@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "turma",
        "numero",
        "data",
        "status",
        "realizada",
        "esta_realizada",
        "gera_apostila",
        "modo_aula",
        "ordem",
    )
    list_filter = ("status", "realizada", "gera_apostila", "turma")
    search_fields = ("titulo", "turma__nome")
    readonly_fields = ("criado_em", "atualizado_em")
    ordering = ("turma", "ordem", "numero")

    @admin.display(description="Pública?")
    def esta_realizada(self, obj):
        return obj.status == "publicada"

    esta_realizada.boolean = True

    @admin.display(description="Modo")
    def modo_aula(self, obj):
        from core.validadores import detectar_modo
        return detectar_modo(obj.conteudo).title()
