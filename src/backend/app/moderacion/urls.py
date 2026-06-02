# moderacion/urls.py
from django.urls import path
from .views import (
    AdminDashboardView,
    UsuarioListView,
    UsuarioDetailView,
    RecetaAdminListView,
    RecetaAdminDetailView,
    ReporteAdminListView,
    ReporteDetailView,
    ReporteCreateView,
)

urlpatterns = [
    # Panel de administrador
    path("admin/", AdminDashboardView.as_view(), name="admin-dashboard"),
    
    # Usuarios (admin)
    path("admin/usuarios/", UsuarioListView.as_view(), name="admin-usuarios-list"),
    path("admin/usuarios/<int:pk>/", UsuarioDetailView.as_view(), name="admin-usuarios-detail"),
    
    # Recetas (admin)
    path("admin/recetas/", RecetaAdminListView.as_view(), name="admin-recetas-list"),
    path("admin/recetas/<int:pk>/", RecetaAdminDetailView.as_view(), name="admin-recetas-detail"),
    
    # Reportes (admin)
    path("admin/reportes/", ReporteAdminListView.as_view(), name="admin-reportes-list"),
    path("admin/reportes/<int:pk>/", ReporteDetailView.as_view(), name="admin-reporte-detail"),
    
    # Crear reporte (público)
    path("reportes/", ReporteCreateView.as_view(), name="reporte-create"),
]