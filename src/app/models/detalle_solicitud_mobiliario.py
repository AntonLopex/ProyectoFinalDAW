from extensions import db

class DetalleSolicitudMobiliario(db.Model):
    __tablename__ = "detalle_solicitud_mobiliario"
 
    id = db.Column(db.Integer, primary_key=True)
    solicitud_id = db.Column(db.Integer, db.ForeignKey("solicitudes.id"), nullable=False)
    mobiliario_id = db.Column(db.Integer, db.ForeignKey("mobiliarios.id"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    precio_total = db.Column(db.Numeric(10, 2), nullable=False, default = 0)
 
    # Relaciones
    solicitud = db.relationship("Solicitud", back_populates="detalles_mobiliario")
    mobiliario = db.relationship("Mobiliario", back_populates="detalles_solicitud")
 
    def __repr__(self):
        return f"<DetalleSolicitudMobiliario {self.id} - Solicitud {self.solicitud_id}>"