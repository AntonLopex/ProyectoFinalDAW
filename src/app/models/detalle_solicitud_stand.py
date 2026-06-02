from extensions import db


class DetalleSolicitudStand(db.Model):
    __tablename__ = "detalle_solicitud_stand"

    id = db.Column(db.Integer, primary_key=True)
    solicitud_id = db.Column(db.Integer, db.ForeignKey("solicitudes.id"), nullable=False)
    stand_id = db.Column(db.Integer, db.ForeignKey("stands.numero_stand"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    precio_total = db.Column(db.Numeric(10, 2), nullable = False, default = 0)

    # Relaciones
    solicitud = db.relationship("Solicitud", back_populates="detalles_stand")
    stand = db.relationship("Stand", back_populates="detalles_solicitud")

    def __repr__(self):
        return f"<DetalleSolicitudStand {self.id} - Solicitud {self.solicitud_id} - Stand {self.stand_id}>"