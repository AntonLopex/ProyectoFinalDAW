from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Usuario


class SessionAuthentication(BaseAuthentication):

    def authenticate(self, request):
        usuario_id = request.session.get("usuario_id")

        if not usuario_id:
            return None

        try:
            usuario = Usuario.objects.get(id=usuario_id)

        except Usuario.DoesNotExist:
            request.session.flush()
            return None

        return (usuario, None)