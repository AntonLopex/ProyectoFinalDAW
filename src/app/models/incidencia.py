from extensions import db
from datetime import datetime


class Incidencia(db.Model):
    __tablename__ = "incidencias"

    id = db.Column(db.Integer, primary_key=True)

    titulo = db.Column(db.String(250), nullable = False)

    descripcion = db.Column(db.Text, nullable=False)

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    fecha_creacion = db.Column(
        db.DateTime,
        default=datetime.now,
        nullable=False
    )

    estado = db.Column(
        db.Enum('pendiente', 'revisada', name='estado_incidencia'),
        nullable=False,
        default='pendiente'
    )

    # Relación con Usuario
    usuario = db.relationship(
        "Usuario",
        backref=db.backref("incidencias", lazy="dynamic")
    )

    def __repr__(self):
        return f"<Incidencia {self.id} - Usuario {self.usuario_id} - Estado {self.estado}>"