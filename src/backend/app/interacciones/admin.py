from django.contrib import admin
from .models import Comentario, Like, Favorito
from olea.admin_config import BaseAdmin, TimestampAdminMixin

# Register your models here.

@admin.register(Comentario)
class ComentarioAdmin(TimestampAdminMixin, BaseAdmin):
    list_display = ("id", "usuario", "receta", "visible", "created_at")
    list_filter = ("visible", "created_at")
    search_fields = ("contenido", "usuario__username", "receta__titulo")
    list_editable = ("visible",)
    autocomplete_fields = ("usuario", "receta")

@admin.register(Like)
class LikeAdmin(BaseAdmin):
    list_display = ("id", "usuario", "receta")
    search_fields = ("usuario__username", "receta__titulo")
    autocomplete_fields = ("usuario", "receta")

@admin.register(Favorito)
class FavoritoAdmin(BaseAdmin):
    list_display = ("id", "usuario", "receta")
    search_fields = ("usuario__username", "receta__titulo")
    autocomplete_fields = ("usuario", "receta")