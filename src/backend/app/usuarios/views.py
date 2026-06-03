from django.contrib.auth.hashers import check_password, make_password

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication

from utils.utils import get_logged_user
from .permissions import IsLoggedIn
from recetas.permissions import IsAdminOrRegistrado
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Usuario
from .serializers import (
    RegisterSerializer,
    UsuarioSerializer,
    MiPerfilSerializer
)

from .emails import send_welcome_email

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_welcome_email(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        nombre_usuario = request.data.get("nombre_usuario")
        password = request.data.get("password")

        if not nombre_usuario or not password:
            return Response(
                {"error": "Nombre de usuario y contraseña requeridos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            usuario = Usuario.objects.get(nombre_usuario = nombre_usuario)
        except Usuario.DoesNotExist:
            return Response(
                {"error": "Credenciales inválidas."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not check_password(password, usuario.password_hash):
            return Response(
                {"error": "Credenciales inválidas."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Guardar el id del usuario en la sesión
        request.session["usuario_id"] = usuario.id
        request.session.save()

        return Response(UsuarioSerializer(usuario).data)


class LogoutView(APIView):
    permission_classes = [IsLoggedIn]

    def post(self, request):
        request.session.flush()
        return Response({"mensaje": "Sesión cerrada correctamente."})

class MeView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):

        user_id = request.session.get("usuario_id")

        if not user_id:
            return Response(None)

        try:
            usuario = Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            return Response(None)

        return Response(UsuarioSerializer(usuario).data)
    

class MyProfileView(APIView):
    """
    Devuelve y actualiza el perfil del usuario logueado.
    URL: /usuarios/mi-perfil/
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        user = get_logged_user(request)
        serializer = UsuarioSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = get_logged_user(request)
        serializer = UsuarioSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Si se subió una nueva foto, borrar la antigua
            if "foto_perfil" in request.data and user.foto_perfil:
                user.foto_perfil.delete(save=False)
            
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatePasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = get_logged_user(request)
        password_actual = request.data.get("password_actual")
        password_nueva = request.data.get("password_nueva")
        password_confirmar = request.data.get("password_confirmar")

        # Verificar contraseña actual usando tu sistema de hash
        if not check_password(password_actual, user.password_hash):
            return Response(
                {"detail": "Contraseña actual incorrecta"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar que las nuevas coinciden
        if password_nueva != password_confirmar:
            return Response(
                {"detail": "Las nuevas contraseñas no coinciden"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Actualizar contraseña usando make_password
        user.password_hash = make_password(password_nueva)
        user.save()

        return Response({"detail": "Contraseña actualizada correctamente"})
    


class MiPerfilView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        usuario = get_logged_user(request)
        serializer = MiPerfilSerializer(usuario, context={"request": request})
        return Response({
            "usuario": {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "apellido1": usuario.apellido1,
                "apellido2": usuario.apellido2,
                "nombre_usuario": usuario.nombre_usuario,
                "email": usuario.email,
                "foto_perfil": request.build_absolute_uri(usuario.foto_perfil.url) if usuario.foto_perfil else None,
                "biografia_y_enlaces": usuario.biografia_y_enlaces,
                "rol": usuario.rol,
            },
            "strikes_count": usuario.strikes_recibidos.count(),
            "likes_recetas": serializer.data.get("likes_recetas", []),
            "favoritos_recetas": serializer.data.get("favoritos_recetas", []),
        })