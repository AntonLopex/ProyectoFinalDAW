from rest_framework.permissions import BasePermission


class IsLoggedIn(BasePermission):

    def has_permission(self, request, view):

        return bool(
            request.session.get("usuario_id")
        )