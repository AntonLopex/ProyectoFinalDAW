from rest_framework import serializers
from recetas.models import Receta
from recetas.serializers import RecetaPerfilSerializer
from .models import Usuario
from utils.utils import generate_unique_username

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    nombre = serializers.CharField(write_only=True)
    apellidos = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ["id", "nombre", "apellidos", "email", "password", "nombre_usuario"]
        extra_kwargs = {
            "nombre_usuario": {"read_only": True}
        }

    def create(self, validated_data):

        nombre = validated_data.pop("nombre")

        apellidos = validated_data.pop("apellidos")

        password = validated_data.pop("password")

        username = generate_unique_username(
            nombre,
            apellidos
        )

        # Separar apellidos
        apellidos_split = apellidos.strip().split()

        apellido1 = (
            apellidos_split[0]
            if len(apellidos_split) > 0
            else ""
        )

        apellido2 = (
            apellidos_split[1]
            if len(apellidos_split) > 1
            else ""
        )

        usuario = Usuario(

            nombre=nombre,

            apellido1=apellido1,

            apellido2=apellido2,

            nombre_usuario=username,

            email=validated_data["email"],
        )

        usuario.set_password(password)

        usuario.save()

        return usuario
                
    
class UsuarioSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = [
            "id",
            "nombre",
            "apellido1",
            "apellido2",
            "nombre_usuario",
            "email",
            "foto_perfil",
            "biografia_y_enlaces",
            "rol",
            "full_name",
        ]
        read_only_fields = ["id", "rol"]
    
    def get_full_name(self, obj):
        return f"{obj.nombre} {obj.apellido1} {obj.apellido2}".strip() or obj.nombre_usuario
    
class MiPerfilSerializer(serializers.ModelSerializer):
    likes_recetas = serializers.SerializerMethodField()
    favoritos_recetas = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            "id",
            "nombre",
            "apellido1",
            "apellido2",
            "nombre_usuario",
            "email",
            "foto_perfil",
            "biografia_y_enlaces",
            "rol",
            "likes_recetas",
            "favoritos_recetas",
        ]

    def get_likes_recetas(self, obj):
        recetas_ids = obj.likes.values_list("receta_id", flat=True)
        qs = Receta.objects.filter(id__in=recetas_ids).select_related("usuario").prefetch_related(
            "recetacategoria_set__categoria", "likes", "favoritos", "comentarios"
        )
        return RecetaPerfilSerializer(
            qs,
            many=True,
            context=self.context
        ).data

    def get_favoritos_recetas(self, obj):
        recetas_ids = obj.favoritos.values_list("receta_id", flat=True)
        qs = Receta.objects.filter(id__in=recetas_ids).select_related("usuario").prefetch_related(
            "recetacategoria_set__categoria", "likes", "favoritos", "comentarios"
        )
        return RecetaPerfilSerializer(
            qs,
            many=True,
            context=self.context
        ).data