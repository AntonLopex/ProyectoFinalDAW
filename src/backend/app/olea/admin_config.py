from django.contrib import admin


class BaseAdmin(admin.ModelAdmin):

    list_per_page = 25
    ordering = ("-id",)
    search_fields = ()
    list_display = ("id",)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))

        model_fields = [f.name for f in self.model._meta.fields]

        if "created_at" in model_fields:
            readonly.append("created_at")

        if "updated_at" in model_fields:
            readonly.append("updated_at")

        return tuple(set(readonly))
# 🧩 ADMIN MIXINS OPCIONALES

class TimestampAdminMixin:
    """
    Añade soporte estándar para timestamps si tus modelos los tienen.
    """
    readonly_fields = ("created_at", "updated_at")


class ActiveFilterAdminMixin:
    """
    Añade comportamiento estándar para modelos con campo 'activo'.
    """
    list_filter = ("activo",)
    list_editable = ("activo",)


# 🎨 ADMIN SITE PERSONALIZADO (OPCIONAL)
class CustomAdminSite(admin.AdminSite):
    site_header = "Panel de Administración"
    site_title = "Sistema"
    index_title = "Gestión General del Proyecto"