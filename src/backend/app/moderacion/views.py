from django.db.models import F  # <- Agregar esto
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from usuarios.models import Usuario
from recetas.models import Receta
from interacciones.models import Comentario
from .models import Reporte, StrikeLog
from .serializers import (
    UsuarioSerializer,
    UsuarioCreateUpdateSerializer,
    RecetaAdminSerializer,
    RecetaAdminDetailSerializer,
    ReporteAdminSerializer,
    ReporteCreateSerializer
)


def get_logged_user(request):
    """Obtener usuario de la sesión."""
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return None
    try:
        return Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return None


def check_admin_permission(request):
    """Verificar si el usuario es admin."""
    usuario = get_logged_user(request)
    if not usuario or usuario.rol != Usuario.Rol.ADMIN:
        return False
    return True


# ==================== DASHBOARD ADMIN ====================
class AdminDashboardView(generics.ListAPIView):
    """Dashboard del admin con estadísticas generales."""
    permission_classes = [AllowAny]
    
    def get(self, request):
        usuario = get_logged_user(request)
        if not usuario or usuario.rol != Usuario.Rol.ADMIN:
            return Response(
                {"detail": "Acceso denegado. Se requieren permisos de administrador."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return Response({
            "total_usuarios": Usuario.objects.count(),
            "total_recetas": Receta.objects.count(),
            "recetas_visibles": Receta.objects.filter(visible=True).count(),
            "recetas_ocultas": Receta.objects.filter(visible=False).count(),
            "total_reportes": Reporte.objects.count(),
            "reportes_pendientes": Reporte.objects.filter(estado=Reporte.Estado.PENDIENTE).count(),
            "reportes_revisados": Reporte.objects.filter(estado=Reporte.Estado.REVISADO).count(),
            "total_strikes": StrikeLog.objects.count(),
        })


# ==================== USUARIOS (ADMIN) ====================
class UsuarioListView(generics.ListCreateAPIView):
    """Listar y crear usuarios (admin only)."""
    queryset = Usuario.objects.all().order_by("-created_at")
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UsuarioCreateUpdateSerializer
        return UsuarioSerializer

    def get(self, request, *args, **kwargs):
        usuario = get_logged_user(request)
        if not usuario or usuario.rol != Usuario.Rol.ADMIN:
            return Response(
                {"detail": "Acceso denegado. Se requieren permisos de administrador."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().get(request, *args, **kwargs)


class UsuarioDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Ver, editar y eliminar usuario (admin only)."""
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'  # <- Agregar esto explícitamente

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UsuarioCreateUpdateSerializer
        return UsuarioSerializer

    def get(self, request, *args, **kwargs):
        if not check_admin_permission(request):
            return Response(
                {"detail": "Acceso denegado. Se requieren permisos de administrador."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().get(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        if not check_admin_permission(request):
            return Response(
                {"detail": "Acceso denegado. Se requieren permisos de administrador."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        if not check_admin_permission(request):
            return Response(
                {"detail": "Acceso denegado. Se requieren permisos de administrador."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)

# ==================== RECETAS (ADMIN) ====================
class RecetaAdminListView(generics.ListAPIView):
    """Listar todas las recetas (admin only)."""
    serializer_class = RecetaAdminSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Receta.objects.all().select_related("usuario").prefetch_related("categorias")
        
        # Filtros opcionales
        visible = self.request.query_params.get('visible')
        if visible is not None:
            queryset = queryset.filter(visible=visible.lower() == 'true')
        
        return queryset.order_by("-created_at")

    def get(self, request, *args, **kwargs):
        usuario = get_logged_user(request)
        if not usuario or usuario.rol != Usuario.Rol.ADMIN:
            return Response(
                {"detail": "Acceso denegado. Se requieren permisos de administrador."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().get(request, *args, **kwargs)


class RecetaAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Ver, editar y eliminar receta (admin only)."""
    queryset = Receta.objects.all()
    serializer_class = RecetaAdminDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'  # <- Agregar esto explícitamente

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return RecetaAdminSerializer
        return RecetaAdminDetailSerializer

    def get(self, request, *args, **kwargs):
        if not check_admin_permission(request):
            return Response(
                {"detail": "Acceso denegado. Se requieren permisos de administrador."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().get(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        if not check_admin_permission(request):
            return Response(
                {"detail": "Acceso denegado. Se requieren permisos de administrador."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        if not check_admin_permission(request):
            return Response(
                {"detail": "Acceso denegado. Se requieren permisos de administrador."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)

# ==================== REPORTES (ADMIN) ====================
class ReporteAdminListView(generics.ListAPIView):
    """Listar todos los reportes (admin only)."""
    serializer_class = ReporteAdminSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Reporte.objects.all().select_related(
            "informador", "receta", "comentario"
        )
        
        # Filtros opcionales
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset.order_by("-created_at")

    def get(self, request, *args, **kwargs):
        usuario = get_logged_user(request)
        if not usuario or usuario.rol != Usuario.Rol.ADMIN:
            return Response(
                {"detail": "Acceso denegado. Se requieren permisos de administrador."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().get(request, *args, **kwargs)


class ReporteDetailView(generics.RetrieveUpdateAPIView):
    """Ver y resolver reporte (admin only)."""
    queryset = Reporte.objects.all()
    serializer_class = ReporteAdminSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'  # <- Agregar esto explícitamente

    def get(self, request, *args, **kwargs):
        if not check_admin_permission(request):
            return Response(
                {"detail": "Acceso denegado. Se requieren permisos de administrador."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().get(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """Resolver un reporte (valido/invalido)."""
        if not check_admin_permission(request):
            return Response(
                {"detail": "Acceso denegado. Se requieren permisos de administrador."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reporte = self.get_object()
        admin = get_logged_user(request)
        
        decision = request.data.get('decision')
        motivo_strike = request.data.get('motivo_strike', '').strip()
        
        if decision not in ['valido', 'invalido']:
            return Response(
                {"detail": "Decisión inválida. Debe ser 'valido' o 'invalido'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not motivo_strike:
            return Response(
                {"detail": "El motivo es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if decision == 'valido':
            usuario_sancionado = None
            
            if reporte.receta:
                usuario_sancionado = reporte.receta.usuario
                reporte.receta.delete()
                reporte.receta = None
            
            if reporte.comentario and not usuario_sancionado:
                usuario_sancionado = reporte.comentario.usuario
                reporte.comentario.delete()
                reporte.comentario = None
            
            if usuario_sancionado:
                StrikeLog.objects.create(
                    usuario_sancionado=usuario_sancionado,
                    admin_responsable=admin,
                    motivo=motivo_strike
                )
                usuario_sancionado.strikes_count = F('strikes_count') + 1
                usuario_sancionado.save()
            
            reporte.estado = Reporte.Estado.REVISADO
            reporte.save()
            
            return Response({
                "detail": "Reporte marcado como válido. Contenido eliminado y strike aplicado.",
                "reporte": ReporteAdminSerializer(reporte).data
            }, status=status.HTTP_200_OK)
        
        else:
            if reporte.receta:
                reporte.receta.visible = True
                reporte.receta.save(update_fields=['visible', 'updated_at'])
            
            reporte.estado = Reporte.Estado.REVISADO
            reporte.save()
            
            return Response({
                "detail": "Reporte marcado como inválido. Contenido restaurado.",
                "reporte": ReporteAdminSerializer(reporte).data
            }, status=status.HTTP_200_OK)

# ==================== CREAR REPORTE (PÚBLICO) ====================
class ReporteCreateView(generics.CreateAPIView):
    """Crear un nuevo reporte."""
    queryset = Reporte.objects.all()
    serializer_class = ReporteCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        usuario = get_logged_user(request)
        if not usuario:
            return Response(
                {"detail": "Debes iniciar sesión para enviar reportes."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        receta_id = request.data.get('receta')
        comentario_id = request.data.get('comentario')
        
        receta_obj = None
        if receta_id:
            try:
                receta_obj = Receta.objects.get(id=receta_id)
            except Receta.DoesNotExist:
                return Response(
                    {"detail": "Receta no encontrada."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        
        if comentario_id:
            try:
                Comentario.objects.get(id=comentario_id)
            except Comentario.DoesNotExist:
                return Response(
                    {"detail": "Comentario no encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reporte = serializer.save()
        
        # Si el reporte es PENDIENTE y es para una receta, hacerla invisible
        if reporte.estado == Reporte.Estado.PENDIENTE and receta_obj:
            receta_obj.visible = False
            receta_obj.save(update_fields=['visible', 'updated_at'])
        
        return Response(
            {
                "id": reporte.id,
                "receta": reporte.receta.id if reporte.receta else None,
                "motivo": reporte.motivo,
                "estado": reporte.estado,
                "receta_invisible": receta_obj is not None and receta_obj.visible == False,
                "mensaje": "Reporte enviado con éxito. La receta ha sido ocultada mientras se revisa." if receta_obj else "Reporte enviado con éxito. Gracias por ayudar a la comunidad."
            },
            status=status.HTTP_201_CREATED
        )