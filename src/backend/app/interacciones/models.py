from django.db import models

from usuarios.models import Usuario
from recetas.models import Receta


class Comentario(models.Model):
    receta = models.ForeignKey(
        Receta,
        on_delete=models.CASCADE,
        related_name="comentarios",
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="comentarios",
    )
    contenido = models.TextField()
    visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    def __str__(self):
        return f"Comentario de {self.usuario} en '{self.receta}'"

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ["-created_at"]


class Like(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    receta = models.ForeignKey(
        Receta,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    class Meta:
        unique_together = ("usuario", "receta")
        verbose_name = "Like"
        verbose_name_plural = "Likes"


class Favorito(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="favoritos",
    )
    receta = models.ForeignKey(
        Receta,
        on_delete=models.CASCADE,
        related_name="favoritos",
    )
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        unique_together = ("usuario", "receta")
        verbose_name = "Favorito"
        verbose_name_plural = "Favoritos"