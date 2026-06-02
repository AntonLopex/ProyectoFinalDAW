from datetime import datetime
from extensions import db


class HistorialStand(db.Model):
    __tablename__ = "historial_stands"

    id = db.Column(db.Integer, primary_key=True)

    stand_id = db.Column(
        db.Integer,
        db.ForeignKey("stands.numero_stand"),
        nullable=True
    )

    solicitud_origen_id = db.Column(
        db.Integer,
        db.ForeignKey("solicitudes.id"),
        nullable=True
    )

    solicitud_destino_id = db.Column(
        db.Integer,
        db.ForeignKey("solicitudes.id"),
        nullable=True
    )

    usuario_origen_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=True
    )

    usuario_destino_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=True
    )

    estado_anterior = db.Column(db.String(50), nullable=True)
    estado_nuevo = db.Column(db.String(50), nullable=False)

    accion = db.Column(db.String(50), nullable=False)  # asignacion, desasignacion, cambio_estado

    observacion = db.Column(db.Text, nullable=True)

    fecha = db.Column(db.DateTime, default=datetime.now(), nullable=False)

    # Relaciones (opcionales pero útiles)
    stand = db.relationship("Stand")
    solicitud_origen = db.relationship("Solicitud", foreign_keys=[solicitud_origen_id])
    solicitud_destino = db.relationship("Solicitud", foreign_keys=[solicitud_destino_id])
    usuario_origen = db.relationship("Usuario", foreign_keys=[usuario_origen_id])
    usuario_destino = db.relationship("Usuario", foreign_keys=[usuario_destino_id])

    def __repr__(self):
        return f"<HistorialStand Stand {self.stand_id} {self.accion}>"