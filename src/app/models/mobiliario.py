from extensions import db


class Mobiliario(db.Model):
    __tablename__ = "mobiliarios"

    id = db.Column(db.Integer, primary_key=True)
    solicitud_id = db.Column(db.Integer, db.ForeignKey("solicitudes.id"), nullable=True)
    referencia = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    stock = db.Column(db.Integer, nullable=False, default=0)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    imagen_url   = db.Column(db.String(1000),    nullable=True)

    # Relaciones
    solicitud = db.relationship("Solicitud", back_populates="mobiliarios")
    detalles_solicitud = db.relationship(
        "DetalleSolicitudMobiliario", back_populates="mobiliario", lazy="dynamic"
    )

    def __repr__(self):
        return f"<Mobiliario {self.id} - {self.referencia}>"