from datetime import datetime
from extensions import db
 
 
class Solicitud(db.Model):
    __tablename__ = "solicitudes"
 
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    observaciones = db.Column(db.Text)
    fecha_solicitud = db.Column(db.DateTime, default=lambda: datetime.now())
    estado = db.Column(db.String(50), nullable=False, default="borrador")
    precio_final = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    descuento = db.Column(db.Numeric(10, 2), nullable=False, default=0)
 
    # Relaciones
    usuario = db.relationship("Usuario", back_populates="solicitudes")
    detalles_mobiliario = db.relationship(
        "DetalleSolicitudMobiliario",
        back_populates="solicitud",
        cascade="all, delete-orphan",
        lazy="select",
    )
    detalles_stand = db.relationship(
        "DetalleSolicitudStand",
        back_populates="solicitud",
        cascade="all, delete-orphan",
        lazy="select",
    )
    stands = db.relationship("Stand", back_populates="solicitud", lazy="dynamic")
    mobiliarios = db.relationship("Mobiliario", back_populates="solicitud", lazy="dynamic")
    extras = db.relationship("Extra", back_populates="solicitud", cascade="all, delete-orphan")
 
    def __repr__(self):
        return f"<Solicitud {self.id} - Usuario {self.usuario_id} - Estado: {self.estado}>"