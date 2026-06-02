from extensions import db
from .enums import EstadoStandEnum
 
class Stand(db.Model):
    __tablename__ = "stands"
 
    numero_stand = db.Column(db.Integer, nullable=False, primary_key=True)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    dimensiones = db.Column(db.Numeric(10, 2))
    estado = db.Column(db.Enum(EstadoStandEnum), nullable=False, default=EstadoStandEnum.disponible)
    solicitud_id = db.Column(db.Integer, db.ForeignKey("solicitudes.id"), nullable=True)
 
    # Relaciones
    solicitud = db.relationship("Solicitud", back_populates="stands")
    detalles_solicitud = db.relationship(
        "DetalleSolicitudStand", back_populates="stand", lazy="dynamic"
    )
 
    def __repr__(self):
        return f"<Stand {self.id} - Nº{self.numero_stand} - {self.estado.value}>"