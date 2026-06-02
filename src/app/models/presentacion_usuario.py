from extensions import db


class PresentacionUsuario(db.Model):
    __tablename__ = "presentacion_usuario"

    id = db.Column(db.Integer, primary_key=True)
    presentacion_id = db.Column(db.Integer, db.ForeignKey("presentaciones.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)  

    __table_args__ = (
        db.UniqueConstraint("presentacion_id", "usuario_id", name="uq_presentacion_usuario"),
    )

    # Relaciones
    presentacion = db.relationship("Presentacion", back_populates="presentacion_usuarios")
    usuario = db.relationship("Usuario", back_populates="presentacion_usuarios")  

    def __repr__(self):
        return f"<PresentacionUsuario presentacion={self.presentacion_id} usuario={self.usuario_id}>"