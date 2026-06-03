from django.db import models
from django.contrib.auth.hashers import make_password


class Usuario(models.Model):
    class Rol(models.TextChoices):
        REGISTRADO = "registrado", "Registrado"
        ADMIN = "admin", "Admin"
    nombre = models.CharField(max_length=100, default="")
    apellido1 = models.CharField(max_length=150, default="")
    apellido2 = models.CharField(max_length=150, default="")
    nombre_usuario = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    foto_perfil = models.ImageField(upload_to="perfiles/", null=True, blank=True)
    biografia_y_enlaces = models.TextField(null=True, blank=True)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.REGISTRADO)
    strikes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False
    
    @property
    def is_active(self):
        return True

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def __str__(self):
        return self.nombre_usuario

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"