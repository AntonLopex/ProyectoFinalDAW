from django.contrib import admin
from olea.admin_config import BaseAdmin, TimestampAdminMixin

from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(TimestampAdminMixin, BaseAdmin):
    list_display = (
        "id",
        "nombre_usuario",
        "email",
        "rol",
        "strikes_count",
    )

    list_filter = (
        "rol",
        "strikes_count",
    )

    search_fields = (
        "nombre_usuario",
        "email",
    )

    ordering = ("nombre_usuario",)

    list_editable = ("rol", "strikes_count")

    readonly_fields = ("password_hash",)

    fieldsets = (
        ("Información básica", {
            "fields": ("nombre_usuario", "email", "foto_perfil")
        }),
        ("Seguridad", {
            "fields": ("password_hash", "rol", "strikes_count")
        }),
        ("Perfil", {
            "fields": ("biografia_y_enlaces",)
        }),
    )