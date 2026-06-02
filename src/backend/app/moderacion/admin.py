from django.contrib import admin
from olea.admin_config import BaseAdmin, TimestampAdminMixin

from .models import Reporte, StrikeLog

# Register your models here.
@admin.register(Reporte)
class ReporteAdmin(TimestampAdminMixin, BaseAdmin):
    list_display = ("id", "informador", "receta", "comentario", "estado", "created_at")
    list_filter = ("estado", "created_at")
    search_fields = (
        "motivo",
        "informador__username",
        "receta__titulo",
        "comentario__contenido",
    )
    autocomplete_fields = ("informador", "receta", "comentario")

    actions = ["marcar_como_revisado"]

    @admin.action(description="Marcar como revisado")
    def marcar_como_revisado(self, request, queryset):
        queryset.update(estado=Reporte.Estado.REVISADO)

@admin.register(StrikeLog)
class StrikeLogAdmin(TimestampAdminMixin, BaseAdmin):
    list_display = (
        "id",
        "usuario_sancionado",
        "admin_responsable",
        "motivo",
        "fecha",
    )
    list_filter = ("fecha",)
    search_fields = (
        "usuario_sancionado__username",
        "admin_responsable__username",
        "motivo",
    )
    autocomplete_fields = ("usuario_sancionado", "admin_responsable")

    readonly_fields = ("fecha",)