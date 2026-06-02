import json

from rest_framework import serializers
from utils.utils import get_logged_user

from .models import Receta, Categoria
from interacciones.models import Comentario, Like, Favorito


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre"]


class ComentarioSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source="usuario.nombre_usuario", read_only=True)

    class Meta:
        model = Comentario
        fields = ["id", "usuario_nombre", "contenido", "visible", "created_at"]


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre"]


class RecetaListSerializer(serializers.ModelSerializer):
    # Categorías
    categorias = CategoriaSerializer(many=True, read_only=True)

    # Campos de usuario
    usuario_nombre = serializers.CharField(source="usuario.nombre", read_only=True)
    usuario_username = serializers.CharField(source="usuario.nombre_usuario", read_only=True)
    usuario_id = serializers.IntegerField(source="usuario.id", read_only=True)

    # Contadores
    likes_count = serializers.SerializerMethodField()
    comentarios_count = serializers.SerializerMethodField()

    # Comentarios asociados (solo los últimos 5)
    comentarios = serializers.SerializerMethodField()

    # Flags para el usuario actual (like y favorito)
    usuario_like = serializers.SerializerMethodField()
    usuario_favorito = serializers.SerializerMethodField()
    usuario_foto = serializers.SerializerMethodField()

    class Meta:
        model = Receta
        fields = [
            "id",
            "titulo",
            "descripcion",
            "ingredientes",
            "elaboracion",
            "dificultad",
            "raciones",
            "tiempo_de_elaboracion",
            "imagen",
            "visible",
            "categorias",
            "usuario_nombre",
            "usuario_foto",
            "usuario_username",
            "usuario_id",
            "created_at",
            "likes_count",
            "comentarios_count",
            "comentarios",
            "usuario_like",
            "usuario_favorito",
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comentarios_count(self, obj):
        return obj.comentarios.filter(visible=True).count()

    def get_comentarios(self, obj):
        # Devuelve los últimos 5 comentarios públicos
        qs = obj.comentarios.filter(visible=True).order_by("-created_at")[:5]
        return ComentarioSerializer(qs, many=True).data

    def get_usuario_like(self, obj):
        request = self.context["request"]
        user = get_logged_user(request)

        if not user:
            return False

        return obj.likes.filter(usuario=user).exists()

    def get_usuario_favorito(self, obj):
        request = self.context["request"]
        user = get_logged_user(request)

        if not user:
            return False

        return obj.favoritos.filter(usuario=user).exists()

    def get_usuario_foto(self, obj):
        request = self.context.get("request")
        if obj.usuario.foto_perfil and request:
            return request.build_absolute_uri(obj.usuario.foto_perfil.url)
        return None
    
class RecetaPerfilSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source="usuario.nombre_usuario", read_only=True)
    usuario_foto = serializers.SerializerMethodField()
    categorias = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comentarios_count = serializers.SerializerMethodField()
    favoritos_count = serializers.SerializerMethodField()
    usuario_like = serializers.SerializerMethodField()
    usuario_favorito = serializers.SerializerMethodField()

    class Meta:
        model = Receta
        fields = [
            "id",
            "titulo",
            "descripcion",
            "imagen",
            "usuario_username",
            "usuario_foto",
            "categorias",
            "likes_count",
            "comentarios_count",
            "favoritos_count",
            "usuario_like",
            "usuario_favorito",
        ]

    def get_usuario_foto(self, obj):
        request = self.context.get("request")
        if obj.usuario and obj.usuario.foto_perfil:
            if request:
                return request.build_absolute_uri(obj.usuario.foto_perfil.url)
            return obj.usuario.foto_perfil.url
        return None

    def get_categorias(self, obj):
        rels = obj.recetacategoria_set.select_related("categoria").all()
        return [{"id": r.categoria.id, "nombre": r.categoria.nombre} for r in rels]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comentarios_count(self, obj):
        return obj.comentarios.filter(visible=True).count()

    def get_favoritos_count(self, obj):
        return obj.favoritos.count()

    def get_usuario_like(self, obj):
        user = self.context.get("usuario_logueado")
        if user:
            return obj.likes.filter(usuario=user).exists()
        return False

    def get_usuario_favorito(self, obj):
        user = self.context.get("usuario_logueado")
        if user:
            return obj.favoritos.filter(usuario=user).exists()
        return False


class RecetaCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para CREAR recetas con imagen upload.
    """
    imagen = serializers.ImageField(write_only=True, required=True)
    ingredientes = serializers.CharField(write_only=True)
    elaboracion = serializers.CharField(write_only=True)
    categoria = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        write_only=True
    )

    class Meta:
        model = Receta
        fields = [
            'titulo', 'tiempo_de_elaboracion', 'dificultad', 
            'raciones', 'categoria', 'ingredientes', 'elaboracion', 'imagen'
        ]

    def create(self, validated_data):
        # Extraer categoría (es un solo objeto, no lista)
        categoria_obj = validated_data.pop('categoria', None)
        
        # Parsear JSON string a Python list
        ingredientes = json.loads(validated_data.pop('ingredientes', '[]'))
        elaboracion = json.loads(validated_data.pop('elaboracion', '[]'))
        
        # Crear la receta
        receta = Receta.objects.create(
            ingredientes=ingredientes,
            elaboracion=elaboracion,
            **validated_data
        )
        
        # Añadir categoría (ManyToMany)
        if categoria_obj:
            receta.categorias.add(categoria_obj)
        
        return receta
    
     
class CategoriaCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para CREAR categorías (solo nombre).
    """
    class Meta:
        model = Categoria
        fields = ['nombre']
    
    def create(self, validated_data):
        nombre = validated_data.get('nombre').strip()
        
        # Verificar si ya existe
        if Categoria.objects.filter(nombre__iexact=nombre).exists():
            raise serializers.ValidationError({
                'nombre': 'Ya existe una categoría con este nombre'
            })
        
        return Categoria.objects.create(nombre=nombre)