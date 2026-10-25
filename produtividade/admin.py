from django.contrib import admin

from .models import (
    Equipamento,
    Equipe,
    Obra,
    RegistroProdutividade,
    RegistroTelemetria,
    Servico,
    HistoricoPrevisao, 
    FechamentoMensal
)


@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = ("nome", "quantidade_funcionarios")
    search_fields = ("nome",)


@admin.register(Obra)
class ObraAdmin(admin.ModelAdmin):
    list_display = ("nome", "local")
    search_fields = ("nome", "local")


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ("nome", "unidade")
    search_fields = ("nome",)


@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ("identificador", "nome", "tipo")
    search_fields = ("identificador", "nome", "tipo")


@admin.register(RegistroProdutividade)
class RegistroProdutividadeAdmin(admin.ModelAdmin):
    list_display = (
        "data",
        "obra",
        "equipe",
        "servico",
        "produtividade",
        "origem",
    )
    list_filter = ("data", "condicao_trabalho", "origem", "obra")


@admin.register(RegistroTelemetria)
class RegistroTelemetriaAdmin(admin.ModelAdmin):
    list_display = (
        "registrado_em",
        "equipamento",
        "obra",
        "horas_operacao",
        "tempo_ocioso",
        "producao",
    )
    list_filter = ("obra", "equipamento")


admin.site.register(HistoricoPrevisao)
admin.site.register(FechamentoMensal)