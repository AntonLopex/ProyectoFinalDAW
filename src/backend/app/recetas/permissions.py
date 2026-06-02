# permissions.py
from rest_framework import permissions
from utils.utils import get_logged_user


class IsAdmin(permissions.BasePermission):
    """
    Permite acceso solo a usuarios con rol 'admin'.
    """
    def has_permission(self, request, view):
        user = get_logged_user(request)
        if not user:
            return False

        rol = getattr(user, "rol", None)
        return rol == "admin"


class IsRegistrado(permissions.BasePermission):
    """
    Permite acceso a usuarios con rol 'registrado' o 'admin'.
    """
    def has_permission(self, request, view):
        user = get_logged_user(request)
        if not user:
            return False

        rol = getattr(user, "rol", None)
        return rol in ["registrado", "admin"]


class IsAdminOrRegistrado(permissions.BasePermission):
    """
    Permite acceso a usuarios con rol 'registrado' o 'admin'.
    """
    def has_permission(self, request, view):
        user = get_logged_user(request)
        if not user:
            return False

        rol = getattr(user, "rol", None)
        return rol in ["registrado", "admin"]