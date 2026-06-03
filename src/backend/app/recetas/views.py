from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from django.db import models


from .models import Receta, Categoria
from interacciones.models import Like, Comentario
from usuarios.models import Usuario
from .permissions import IsAdmin, IsRegistrado, IsAdminOrRegistrado

from .serializers import RecetaListSerializer, ComentarioSerializer, CategoriaSerializer, RecetaCreateSerializer, CategoriaCreateSerializer
from usuarios.serializers import UsuarioSerializer


def get_logged_user(request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return None
    try:
        return Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return None



class RecetaAPIView(generics.ListCreateAPIView):
    """
    LISTAR (GET) y CREAR (POST) recetas.
    """
    queryset = (
        Receta.objects.filter(visible=True)
        .select_related("usuario")
        .prefetch_related("categorias", "likes", "favoritos", "comentarios")
    )
    serializer_class = RecetaListSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RecetaCreateSerializer
        return RecetaListSerializer

    def perform_create(self, serializer):
        # Obtener usuario de la sesión
        usuario_id = self.request.session.get("usuario_id")
        if not usuario_id:
            raise UsuarioSerializer.ValidationError({"detail": "Debes iniciar sesión."})
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            serializer.save(usuario=usuario)
        except Usuario.DoesNotExist:
            raise UsuarioSerializer.ValidationError({"detail": "Usuario no encontrado."})

class RecetaDetailView(generics.RetrieveAPIView):
    queryset = Receta.objects.all()
    serializer_class = RecetaListSerializer
    lookup_field = "id"

# 3) Endpoint de like
@api_view(["POST"])
@permission_classes([IsAdminOrRegistrado])
def receta_like_view(request, receta_id):
    user = get_logged_user(request)
    if not user:
        return Response(
            {"detail": "Debes iniciar sesión."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    receta = get_object_or_404(Receta, id=receta_id, visible=True)

    like, created = Like.objects.get_or_create(usuario=user, receta=receta)

    if created:
        action = "liked"
    else:
        like.delete()
        action = "unliked"

    return Response(
        {
            "action": action,
            "likes_count": receta.likes.count(),
            "usuario_like": action == "liked",
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAdminOrRegistrado])
def comentarios_receta_view(request, receta_id):
    """
    Todos los comentarios visibles de una receta.
    Usado en el modal de comentarios.
    """
    receta = get_object_or_404(Receta, id=receta_id, visible=True)

    comentarios = (
        Comentario.objects
        .filter(receta=receta, visible=True)
        .order_by("-created_at")
    )

    serializer = ComentarioSerializer(comentarios, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAdminOrRegistrado])
def crear_comentario_view(request):
    """
    Crear un comentario para una receta.
    request.data debe incluir:
    - receta: id de la receta
    - contenido: texto del comentario
    """
    user = get_logged_user(request)
    if not user:
        return Response(
            {"detail": "Debes iniciar sesión."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    data = request.data
    receta_id = data.get("receta")
    contenido = data.get("contenido")

    if not receta_id or not contenido:
        return Response(
            {"detail": "Faltan campos obligatorios."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    receta = get_object_or_404(Receta, id=receta_id, visible=True)

    comentario = Comentario.objects.create(
        receta=receta,
        usuario=user,
        contenido=contenido.strip(),
        visible=True,
    )

    serializer = ComentarioSerializer(comentario)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class ComentariosPorRecetaView(generics.ListCreateAPIView):
    serializer_class = ComentarioSerializer
    permission_classes = [IsAdminOrRegistrado]

    def get_queryset(self):
        receta_id = self.kwargs["receta_id"]
        return Comentario.objects.filter(receta__id=receta_id).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(
            receta_id=self.kwargs["receta_id"],
            usuario=self.request.user
        )

class CategoriaListView(generics.ListCreateAPIView):
    """
    LISTAR (GET) y CREAR (POST) categorías.
    """
    queryset = Categoria.objects.all().order_by("nombre")
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CategoriaCreateSerializer
        return CategoriaSerializer

    def perform_create(self, serializer):
        serializer.save()


class RecetasPorCategoriaAPIView(ListAPIView):
    serializer_class = RecetaListSerializer
    permission_classes = [IsAdminOrRegistrado]

    def get_queryset(self):
        categoria_id = self.kwargs["categoria_id"]

        return (
            Receta.objects.filter(
                visible=True,
                categorias__id=categoria_id
            )
            .distinct()
            .select_related("usuario")
            .prefetch_related(
                "categorias",
                "likes",
                "favoritos",
                "comentarios",
            )
        )
        
class TopRecetasAPIView(generics.ListAPIView):
    """
    Devuelve las 6 recetas con más likes.
    """
    serializer_class = RecetaListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            Receta.objects.filter(visible=True)
            .select_related("usuario")
            .prefetch_related("categorias", "likes", "favoritos", "comentarios")
            .annotate(likes_count=Count("likes"))
            .order_by("-likes_count")[:6]
        )
        
class UserProfileView(generics.ListAPIView):
    """
    Devuelve todas las recetas de un usuario específico.
    URL: /recetas/perfil/<username>/
    """
    serializer_class = RecetaListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        username = self.kwargs["username"]
        return (
            Receta.objects.filter(usuario__nombre_usuario=username, visible=True)
            .select_related("usuario")
            .prefetch_related("categorias", "likes", "favoritos", "comentarios")
            .annotate(likes_count=Count("likes"))
            .order_by("-created_at")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        username = self.kwargs["username"]
        
        try:
            user = Usuario.objects.get(nombre_usuario=username)
        except Usuario.DoesNotExist:
            return Response({"detail": "Usuario no encontrado"}, status=404)
        
        serializer = self.get_serializer(queryset, many=True)
        
        # Calcular total likes
        total_likes = queryset.aggregate(total=Count("likes"))["total"] or 0
        
        return Response({
            "usuario": UsuarioSerializer(user).data,
            "recetas": serializer.data,
            "total_recetas": queryset.count(),
            "total_likes": total_likes,
        })


class SearchUserView(APIView):
    """
    Busca usuarios por nombre_usuario o nombre.
    URL: /recetas/buscar-usuario/?q=<query>
    """
    permission_classes = [AllowAny]

    def get(self, request):
        query = self.request.query_params.get("q", "")
        if len(query) < 2:
            return Response({"usuarios": []})
        
        users = Usuario.objects.filter(
            models.Q(nombre_usuario__icontains=query) | 
            models.Q(nombre__icontains=query) |
            models.Q(apellido1__icontains=query)
        )[:10]
        
        data = [
            {
                "id": user.id,
                "nombre_usuario": user.nombre_usuario,
                "nombre": user.nombre,
                "apellido1": user.apellido1,
                "apellido2": user.apellido2,
                "full_name": f"{user.nombre} {user.apellido1} {user.apellido2}".strip() or user.nombre_usuario,
            }
            for user in users
        ]
        
        return Response({"usuarios": data})
    

class CategoriaCreateView(generics.CreateAPIView):
    """
    Crear una nueva categoría.
    Solo nombre es requerido.
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        categoria = serializer.save()
        
        return Response(
            CategoriaSerializer(categoria).data,
            status=status.HTTP_201_CREATED
        )


class RecetaCreateView(generics.CreateAPIView):
    """
    Crear una nueva receta con imagen upload.
    Usa multipart/form-data.
    """
    queryset = Receta.objects.all()
    serializer_class = RecetaCreateSerializer
    permission_classes = [IsAdminOrRegistrado]

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def create(self, request, *args, **kwargs):
        # Obtener usuario de la sesión
        usuario = get_logged_user(request)
        if not usuario:
            return Response(
                {"detail": "Debes iniciar sesión para crear recetas."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Guardar con el usuario
        receta = serializer.save(usuario=usuario)
        
        return Response(
            RecetaListSerializer(receta).data,
            status=status.HTTP_201_CREATED
        )