from django.contrib import admin
from olea.admin_config import BaseAdmin, TimestampAdminMixin

from .models import Categoria, Receta, RecetaCategoria

@admin.register(Categoria)
class CategoriaAdmin(BaseAdmin):
    list_display = ("id", "nombre")
    search_fields = ("nombre",)
    ordering = ("nombre",)

@admin.register(Receta)
class RecetaAdmin(TimestampAdminMixin, BaseAdmin):
    list_display = (
        "id",
        "titulo",
        "usuario",
        "dificultad",
        "visible",
    )

    list_filter = (
        "dificultad",
        "visible",
        "categorias",
    )

    search_fields = (
        "titulo",
        "descripcion",
        "usuario__username",
    )

    autocomplete_fields = ("usuario", "categorias")

    list_editable = ("visible",)

@admin.register(RecetaCategoria)
class RecetaCategoriaAdmin(BaseAdmin):
    list_display = ("id", "receta", "categoria")
    search_fields = ("receta__titulo", "categoria__nombre")
    autocomplete_fields = ("receta", "categoria")