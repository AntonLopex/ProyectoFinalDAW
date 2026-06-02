from django.db import models

from usuarios.models import Usuario
from recetas.models import Receta
from interacciones.models import Comentario


class Reporte(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        REVISADO = "revisado", "Revisado"

    informador = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="reportes_enviados",
    )
    receta = models.ForeignKey(
        Receta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reportes",
    )
    comentario = models.ForeignKey(
        Comentario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reportes",
    )
    motivo = models.CharField(max_length=500)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)
    def __str__(self):
        return f"Reporte #{self.pk} — {self.estado}"

    class Meta:
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
        ordering = ["-created_at"]


class StrikeLog(models.Model):
    usuario_sancionado = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="strikes_recibidos",
    )
    admin_responsable = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="strikes_emitidos",
    )
    motivo = models.CharField(max_length=500)
    fecha = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    def __str__(self):
        return f"Strike a {self.usuario_sancionado} por {self.admin_responsable}"

    class Meta:
        verbose_name = "Strike Log"
        verbose_name_plural = "Strike Logs"
        ordering = ["-fecha"]