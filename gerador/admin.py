from django.contrib import admin

from .models import MaterialEntrada, SessaoGeracao


class MaterialEntradaInline(admin.TabularInline):
    model = MaterialEntrada
    extra = 0
    readonly_fields = ("tipo", "papel_rco", "conteudo_extraido", "ordem")


@admin.register(SessaoGeracao)
class SessaoGeracaoAdmin(admin.ModelAdmin):
    list_display = ("id", "disciplina", "modo", "num_aulas", "provider", "status", "criado_em")
    list_filter = ("modo", "provider", "status", "nivel")
    search_fields = ("disciplina__nome",)
    readonly_fields = ("tokens_usados", "custo_estimado", "criado_em", "atualizado_em")
    inlines = [MaterialEntradaInline]
