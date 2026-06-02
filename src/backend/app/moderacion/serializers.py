from rest_framework import serializers
from usuarios.models import Usuario
from recetas.models import Receta, Categoria
from .models import Reporte, StrikeLog
from interacciones.models import Comentario


class UsuarioSerializer(serializers.ModelSerializer):
    recetas_count = serializers.IntegerField(source="recetas.count", read_only=True)
    reportes_count = serializers.IntegerField(source="reportes_enviados.count", read_only=True)

    es_admin = serializers.SerializerMethodField()
    es_registrado = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'nombre_usuario', 'nombre', 'apellido1', 'apellido2',
            'email', 'foto_perfil', 'es_admin', 'es_registrado',
            'biografia_y_enlaces', 'recetas_count', 'reportes_count', 'strikes_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_es_admin(self, obj):
        return obj.rol == Usuario.Rol.ADMIN

    def get_es_registrado(self, obj):
        return obj.rol == Usuario.Rol.REGISTRADO


class UsuarioCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'nombre_usuario', 'nombre', 'apellido1', 'apellido2',
            'email', 'foto_perfil', 'rol',
            'biografia_y_enlaces'
        ]

    def validate_nombre_usuario(self, value):
        if self.instance and self.instance.nombre_usuario != value:
            if Usuario.objects.filter(nombre_usuario=value).exists():
                raise serializers.ValidationError("Este nombre de usuario ya existe.")
        return value

    def validate_email(self, value):
        if self.instance and self.instance.email != value:
            if Usuario.objects.filter(email=value).exists():
                raise serializers.ValidationError("Este email ya existe.")
        return value


class RecetaAdminSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source="usuario.nombre_usuario", read_only=True)
    categorias_nombres = serializers.SerializerMethodField()

    class Meta:
        model = Receta
        fields = [
            'id', 'titulo', 'descripcion', 'usuario', 'usuario_nombre',
            'ingredientes', 'elaboracion', 'raciones', 'tiempo_de_elaboracion',
            'dificultad', 'imagen', 'visible', 'categorias', 'categorias_nombres',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_categorias_nombres(self, obj):
        return [cat.nombre for cat in obj.categorias.all()]


class RecetaAdminDetailSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source="usuario.nombre_usuario", read_only=True)
    categorias_nombres = serializers.SerializerMethodField()

    class Meta:
        model = Receta
        fields = [
            'id', 'titulo', 'descripcion', 'usuario', 'usuario_nombre',
            'ingredientes', 'elaboracion', 'raciones', 'tiempo_de_elaboracion',
            'dificultad', 'imagen', 'visible', 'categorias', 'categorias_nombres',
            'created_at', 'updated_at'
        ]

    def get_categorias_nombres(self, obj):
        return [cat.nombre for cat in obj.categorias.all()]


class ReporteAdminSerializer(serializers.ModelSerializer):
    informador_nombre = serializers.CharField(source="informador.nombre_usuario", read_only=True)
    receta_titulo = serializers.CharField(source="receta.titulo", read_only=True)
    receta_visible = serializers.BooleanField(source="receta.visible", read_only=True)
    comentario_content = serializers.CharField(source="comentario.contenido", read_only=True)

    class Meta:
        model = Reporte
        fields = [
            'id', 'informador', 'informador_nombre', 'receta', 'receta_titulo',
            'receta_visible', 'comentario', 'comentario_content', 'motivo',
            'estado', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ReporteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reporte
        fields = ['receta', 'comentario', 'motivo']
    
    def validate(self, data):
        if not data.get('receta') and not data.get('comentario'):
            raise serializers.ValidationError({
                'detail': 'Debes reportar una receta o un comentario'
            })
        return data
    
    def create(self, validated_data):
        usuario_id = self.context['request'].session.get('usuario_id')
        if not usuario_id:
            raise serializers.ValidationError({
                'detail': 'Debes iniciar sesión para enviar reportes'
            })
        
        try:
            informador = Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError({
                'detail': 'Usuario no encontrado'
            })
        
        return Reporte.objects.create(
            informador=informador,
            **validated_data
        )