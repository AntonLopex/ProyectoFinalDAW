from datetime import datetime, timezone
from extensions import db
from .enums import TipoAccesoEnum


class ControlES(db.Model):
    __tablename__ = "control_es"

    id            = db.Column(db.Integer,              primary_key=True)
    usuario_id    = db.Column(db.Integer,              db.ForeignKey("usuarios.id"), nullable=False)
    hora_entrada  = db.Column(db.DateTime,             default=lambda: datetime.now(), nullable=False)
    hora_salida   = db.Column(db.DateTime,             nullable=True)
    observaciones = db.Column(db.Text,                 nullable=True)
    tipo_acceso   = db.Column(db.Enum(TipoAccesoEnum), nullable=False)  

    usuario = db.relationship("Usuario", back_populates="controles")

    def __repr__(self):
        return f"<ControlES {self.id} – usuario_id={self.usuario_id} entrada={self.hora_entrada}>"
