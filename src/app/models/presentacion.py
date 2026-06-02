from extensions import db


class Presentacion(db.Model):
    __tablename__ = "presentaciones"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    tema = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    aforo = db.Column(db.Integer, nullable=False, default=0)
    organizador = db.Column(db.String(250), nullable = True)

    # Relaciones
    presentacion_usuarios = db.relationship(
        "PresentacionUsuario",
        back_populates="presentacion",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<Presentacion {self.id} - {self.tema}>"