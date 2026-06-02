from django.db import models

from usuarios.models import Usuario


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"


class Receta(models.Model):
    class Dificultad(models.TextChoices):
        FACIL = "facil", "Fácil"
        MEDIA = "media", "Media"
        DIFICIL = "dificil", "Difícil"

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="recetas",
    )
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    ingredientes = models.JSONField(default=list)
    elaboracion = models.JSONField(default=list)
    raciones = models.CharField(max_length=10)
    tiempo_de_elaboracion=models.TimeField(default="00:00:00")
    dificultad = models.CharField(
        max_length=10, choices=Dificultad.choices, default=Dificultad.MEDIA
    )
    imagen = models.ImageField(
    upload_to='recetas/',
    blank=True,
    null=True
    )
    visible = models.BooleanField(default=True)
    categorias = models.ManyToManyField(
        Categoria,
        through="RecetaCategoria",
        related_name="recetas",
    )
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Receta"
        verbose_name_plural = "Recetas"


class RecetaCategoria(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    class Meta:
        unique_together = ("receta", "categoria")
        verbose_name = "Receta-Categoría"
        verbose_name_plural = "Recetas-Categorías"